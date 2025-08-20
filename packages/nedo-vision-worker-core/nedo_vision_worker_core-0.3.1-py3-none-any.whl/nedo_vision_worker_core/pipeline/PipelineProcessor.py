import logging
import time
import threading
import queue
from ..detection.detection_processing.HumanDetectionProcessor import HumanDetectionProcessor
from ..detection.detection_processing.PPEDetectionProcessor import PPEDetectionProcessor
from .PipelineConfigManager import PipelineConfigManager
from .PipelinePrepocessor import PipelinePrepocessor
from ..repositories.WorkerSourcePipelineDebugRepository import WorkerSourcePipelineDebugRepository
from ..repositories.WorkerSourcePipelineDetectionRepository import WorkerSourcePipelineDetectionRepository
from ..streams.VideoStreamManager import VideoStreamManager
from ..ai.VideoDebugger import VideoDebugger
from ..ai.FrameDrawer import FrameDrawer
from ..tracker.TrackerManager import TrackerManager
from ..detection.DetectionManager import DetectionManager
from ..streams.RTMPStreamer import RTMPStreamer


class PipelineProcessor:
    """Handles pipeline processing including preprocessing, AI model inference, tracking, and video stream processing."""

    def __init__(self, pipeline_id, worker_source_id, model, enable_visualization=True):
        """
        Initializes the PipelineProcessor with configurable detection labels.

        :param model: The model to use for inference.
        :param enable_visualization: Flag to enable visualization.
        :param detection_labels: List of object labels to detect.
        """
        self.running = True
        self.video_debugger = VideoDebugger(enable_visualization)
        self.tracker_manager = TrackerManager()
        self.detection_manager = DetectionManager(model)
        self.config_manager = PipelineConfigManager()
        self.preprocessor = PipelinePrepocessor()
        self.detection_processor = None
        self.threshold = 0.7

        self.frame_queue = queue.Queue(maxsize=1)
        self.tracked_objects_render = []
        self.detection_thread = None
        self.frame_counter = 0
        self.frame_drawer = FrameDrawer()
        self.pipeline_id = pipeline_id
        self.worker_source_id = worker_source_id

        self.rtmp_streamer = None

        self.detection_processor_codes = [
            PPEDetectionProcessor.code,
            HumanDetectionProcessor.code,
        ]

        self.debug_flag = False
        self.debug_repo = WorkerSourcePipelineDebugRepository()
        self.detection_repo = WorkerSourcePipelineDetectionRepository()
        
        # Frame recovery mechanism
        self.consecutive_frame_failures = 0
        self.max_consecutive_failures = 150  # 1.5 seconds at 0.01s intervals
        self.last_successful_frame_time = time.time()
        self.stream_recovery_timeout = 30.0  # 30 seconds timeout for stream recovery
        
        # HEVC error tracking
        self.hevc_error_count = 0
        self.last_hevc_recovery = 0
        self.hevc_recovery_cooldown = 30.0  # 30 seconds between HEVC recovery attempts

    def load_model(self, model):
        """
        Load a new AI model into the detection manager.
        This allows runtime model updates without restarting the pipeline.
        
        :param model: The new AI model to load
        """
        logging.info(f"🔄 Loading new model for pipeline {self.pipeline_id}: {model.name if model else 'None'}")
        self.detection_manager.load_model(model)
        
        # Re-initialize detection processor to use the new model configuration
        self._update_detection_processor()
        
        logging.info(f"✅ Model updated for pipeline {self.pipeline_id}")

    def _get_detection_processor_code(self):
        for code in self.detection_processor_codes:
            if self.config_manager.is_feature_enabled(code):
                return code
            
        return None
    
    def _get_detection_processor(self, code):
        if code == PPEDetectionProcessor.code:
            return PPEDetectionProcessor()
        elif code == HumanDetectionProcessor.code:
            return HumanDetectionProcessor()
        else:
            return None
    
    def _update_detection_processor(self):
        code = self._get_detection_processor_code()

        if self.detection_processor and self.detection_processor.code == code:
            return
        
        self.detection_processor = self._get_detection_processor(code)
        if self.detection_processor:
            self.frame_drawer.update_config(
                icons=self.detection_processor.icons,
                violation_labels=self.detection_processor.violation_labels,
                compliance_labels=self.detection_processor.compliance_labels,
            )
            multi_instance_classes = []
            if hasattr(self.detection_processor, 'get_multi_instance_classes'):
                multi_instance_classes = self.detection_processor.get_multi_instance_classes()
            
            self.tracker_manager.update_config(
                attribute_labels=self.detection_processor.labels,
                exclusive_attribute_groups=self.detection_processor.exclusive_labels,
                multi_instance_classes=multi_instance_classes
            )
        
    def _update_config(self):
        self.config_manager.update(self.pipeline_id)
        self.preprocessor.update(self.config_manager)
        self.detection_interval = self._get_detection_interval()
        self._update_detection_processor()
        
        # Reset frame failure counters on config update
        self.consecutive_frame_failures = 0
        self.last_successful_frame_time = time.time()

        ai_model = self.detection_manager.model_metadata

        if self.detection_processor:
            config = self.config_manager.get_feature_config(self.detection_processor.code)
            self.detection_processor.update(self.config_manager, ai_model)
            self.threshold = config.get("minimumDetectionConfidence", 0.7)

            if self.detection_processor.code == HumanDetectionProcessor.code:
                self.frame_drawer.polygons = [((0, 0, 255), p) for p in self.detection_processor.restricted_areas]
        else:
            self.threshold = 0.7
            self.frame_drawer.update_config()
            self.tracker_manager.update_config(
                attribute_labels=[], 
                exclusive_attribute_groups=[], 
                multi_instance_classes=[]
            )

    def process_pipeline(self, video_manager: VideoStreamManager):
        """
        Runs the full pipeline processing including preprocessing, detection and tracking.
        """
        pipeline_id = self.pipeline_id
        worker_source_id = self.worker_source_id

        logging.info(f"🎯 Running pipeline processing for pipeline {pipeline_id} | Source: {worker_source_id}")

        self._update_config()
        
        # Reset failure counters at start
        self.consecutive_frame_failures = 0
        self.last_successful_frame_time = time.time()

        initial_frame = self._wait_for_frame(video_manager)
        if initial_frame is None:
            logging.error(f"❌ Pipeline {pipeline_id} | Source {worker_source_id}: No initial frame available. Exiting...")
            return

        self.rtmp_streamer = RTMPStreamer(pipeline_id)

        # Start detection in a separate thread
        self.detection_thread = threading.Thread(
            target=self._detection_worker,
            name=f"detection-{pipeline_id}"
        )
        self.detection_thread.daemon = True
        self.detection_thread.start()

        try:
            while self.running:
                frame = video_manager.get_frame(worker_source_id)

                if frame is None:
                    if not self._handle_frame_failure(video_manager, worker_source_id):
                        break
                    continue

                # Reset failure counters on successful frame
                self.consecutive_frame_failures = 0
                self.last_successful_frame_time = time.time()

                self.frame_counter += 1

                self.frame_drawer.draw_polygons(frame)
                drawn_frame = self.frame_drawer.draw_frame(
                    frame.copy(),
                    self.tracked_objects_render,
                    with_trails=True,
                    trail_length=int(2 / self.detection_interval)
                )

                if self.debug_flag:
                    tracked_objects_render = self._process_frame(frame)

                    self.debug_repo.update_debug_entries_by_pipeline_id(
                        self.pipeline_id, 
                        self.frame_drawer.draw_frame(
                            frame.copy(),
                            tracked_objects_render
                        ),
                        tracked_objects_render
                    )
                    self.debug_flag = False

                # Check RTMP streamer status before sending frame
                if self.rtmp_streamer:
                    try:
                        self.rtmp_streamer.send_frame(drawn_frame)
                    except Exception as e:
                        logging.error(f"❌ RTMP streaming error: {e}")
                        # Stop RTMP streamer on error
                        self.rtmp_streamer.stop_stream()
                        self.rtmp_streamer = None

                # Only put frame in queue if detection thread is still running
                if self.detection_thread and self.detection_thread.is_alive():
                    if not self.frame_queue.full():
                        self.frame_queue.put(frame, block=False)

                try:
                    self.video_debugger.show_frame(pipeline_id, worker_source_id, drawn_frame)
                except Exception as e:
                    logging.error(f"⚠️ Failed to render frame for pipeline {pipeline_id}: {e}")

                time.sleep(0.01)
        except Exception as e:
            logging.error(f"❌ Error in pipeline {pipeline_id}: {e}", exc_info=True)

    def _process_frame(self, frame):
        dimension = frame.shape[:2]

        processed_frame = self.preprocessor.apply(frame)
        
        class_thresholds = {}
        ai_model = self.detection_manager.model_metadata
        
        if self.detection_processor:
            if self.detection_processor.code == PPEDetectionProcessor.code:
                class_thresholds.update(self.detection_processor.get_class_thresholds())
            elif self.detection_processor.code == HumanDetectionProcessor.code:
                main_threshold = self.detection_processor.get_main_class_threshold(ai_model)
                if main_threshold and ai_model and ai_model.get_main_class():
                    class_thresholds[ai_model.get_main_class()] = main_threshold
        
        detections = self.detection_manager.detect_objects(processed_frame, self.threshold, class_thresholds)    
        detections = self.preprocessor.revert_detections_bboxes(detections, dimension)
        
        if self.detection_processor:
            matched_results = self.detection_processor.process(detections, dimension)
            return self.tracker_manager.track_objects(matched_results)
        else:
            return self.tracker_manager.track_objects(detections)


    def _detection_worker(self):
        """
        Runs detection in a separate thread and updates configuration periodically.
        Applies preprocessing based on pipeline configuration.
        """
        pipeline_id = self.pipeline_id
        worker_source_id = self.worker_source_id
        last_detection_time = time.time()
        last_config_update_time = time.time()  
        config_update_interval = 5  # Update configuration every 5 seconds

        while self.running:
            try:
                frame = self.frame_queue.get(block=True, timeout=1)
                current_time = time.time()

                # Update config periodically
                if (current_time - last_config_update_time) >= config_update_interval:
                    self._update_config()
                    last_config_update_time = current_time 
                    logging.info(f"🔄 Updated pipeline config for {pipeline_id}")

                # Process detection only if enough time has passed since last detection
                # detection_interval is the time in seconds between consecutive detections
                if (current_time - last_detection_time) < self.detection_interval:
                    continue

                last_detection_time = current_time 
                
                if self.detection_processor is None or frame is None or frame.size == 0:
                    self.tracked_objects_render = []
                    continue

                self.tracked_objects_render = self._process_frame(frame)
                
                # Save to database if enabled
                if self.config_manager.is_feature_enabled("db"):
                    self.detection_processor.save_to_db(
                        pipeline_id,
                        worker_source_id,
                        self.frame_counter,
                        self.tracked_objects_render,
                        frame,
                        self.frame_drawer
                    )

                if self.config_manager.is_feature_enabled("webhook") or self.config_manager.is_feature_enabled("mqtt"):
                    self.detection_repo.save_detection(
                        pipeline_id,
                        frame,
                        self.tracked_objects_render,
                        self.frame_drawer
                    )

            except queue.Empty:
                pass
            except Exception as e:
                logging.error(f"❌ Error in detection thread for pipeline {pipeline_id}: {e}", exc_info=True)
    
    def _wait_for_frame(self, video_manager, max_retries=10, sleep_time=3):
        """Waits until a frame is available from the video source."""
        logging.info(f"⏳ Waiting for initial frame from {self.worker_source_id}...")
        
        for retry_count in range(max_retries):
            frame = video_manager.get_frame(self.worker_source_id)
            if frame is not None:
                logging.info(f"✅ Initial frame received from {self.worker_source_id}")
                return frame
            
            # Check if stream exists
            if not video_manager.has_stream(self.worker_source_id):
                logging.error(f"❌ Stream {self.worker_source_id} not found in video manager")
                return None
            
            logging.warning(f"⚠️ Waiting for video stream {self.worker_source_id} (Attempt {retry_count + 1}/{max_retries})...")
            
            # Log stream diagnostics on later attempts
            if retry_count >= 3:
                self._log_stream_diagnostics(video_manager, self.worker_source_id)
            
            time.sleep(sleep_time)

        logging.error(f"❌ Failed to get initial frame from {self.worker_source_id} after {max_retries} attempts")
        return None

    def _handle_frame_failure(self, video_manager, worker_source_id):
        """
        Handle frame retrieval failures with progressive backoff and recovery attempts.
        Returns False if pipeline should stop, True to continue.
        """
        self.consecutive_frame_failures += 1
        
        # Check if stream was removed
        if not video_manager.has_stream(worker_source_id):
            logging.info(f"🛑 Stream {worker_source_id} was removed, stopping pipeline")
            return False
        
        # Check for stream recovery timeout
        time_since_last_frame = time.time() - self.last_successful_frame_time
        if time_since_last_frame > self.stream_recovery_timeout:
            logging.error(f"❌ Stream {worker_source_id} recovery timeout ({self.stream_recovery_timeout}s). Stopping pipeline.")
            return False
        
        # Progressive logging and backoff
        if self.consecutive_frame_failures <= 10:
            # First 10 failures: minimal logging, fast retry
            if self.consecutive_frame_failures % 5 == 1:  # Log every 5th failure
                logging.debug(f"⚠️ No frame available for {worker_source_id} (attempt {self.consecutive_frame_failures})")
            time.sleep(0.01)
        elif self.consecutive_frame_failures <= 50:
            # 11-50 failures: moderate logging, slightly longer wait
            if self.consecutive_frame_failures % 10 == 1:  # Log every 10th failure
                logging.warning(f"⚠️ No frame available for {worker_source_id} (attempt {self.consecutive_frame_failures}). Stream may be reconnecting...")
            time.sleep(0.05)
        elif self.consecutive_frame_failures <= self.max_consecutive_failures:
            # 51-150 failures: more frequent logging, longer wait
            if self.consecutive_frame_failures % 20 == 1:  # Log every 20th failure
                logging.warning(f"⚠️ Persistent frame issues for {worker_source_id} (attempt {self.consecutive_frame_failures}). Checking stream health...")
                self._log_stream_diagnostics(video_manager, worker_source_id)
                
                # Attempt HEVC recovery on severe persistent failures (every 60 failures to avoid too frequent reconnections)
                if self.consecutive_frame_failures % 60 == 1:
                    # Check if we should attempt HEVC recovery based on error patterns and cooldown
                    if self._should_attempt_hevc_recovery(video_manager, worker_source_id):
                        logging.info(f"🔧 Attempting HEVC-specific recovery for persistent frame failures...")
                        recovery_success = self._handle_hevc_recovery(video_manager, worker_source_id)
                        if recovery_success:
                            logging.info(f"✅ HEVC recovery successful, continuing pipeline...")
                            return True  # Continue processing after successful recovery
                    
            time.sleep(0.1)
        else:
            # Over max failures: critical logging and stop
            logging.error(f"❌ Too many consecutive frame failures for {worker_source_id} ({self.consecutive_frame_failures}). Stopping pipeline.")
            self._log_stream_diagnostics(video_manager, worker_source_id)
            return False
        
        return True
    
    def _log_stream_diagnostics(self, video_manager, worker_source_id):
        """Log diagnostic information about the stream state."""
        try:
            stream_url = video_manager.get_stream_url(worker_source_id)
            is_file = video_manager.is_video_file(worker_source_id)
            
            # Get stream object for more detailed diagnostics
            if hasattr(video_manager, 'streams') and worker_source_id in video_manager.streams:
                stream = video_manager.streams[worker_source_id]
                state = stream.get_state() if hasattr(stream, 'get_state') else "unknown"
                is_connected = stream.is_connected() if hasattr(stream, 'is_connected') else "unknown"
                
                logging.info(f"📊 Stream diagnostics for {worker_source_id}:")
                logging.info(f"   URL: {stream_url}")
                logging.info(f"   Type: {'Video file' if is_file else 'Live stream'}")
                logging.info(f"   State: {state}")
                logging.info(f"   Connected: {is_connected}")
                logging.info(f"   Time since last frame: {time.time() - self.last_successful_frame_time:.1f}s")
                
                # Check for HEVC/codec specific issues
                if hasattr(stream, 'get_codec_info'):
                    codec_info = stream.get_codec_info()
                    if codec_info:
                        logging.info(f"   Codec: {codec_info}")
                        if 'hevc' in str(codec_info).lower() or 'h265' in str(codec_info).lower():
                            logging.warning(f"   ⚠️ HEVC stream detected - may experience QP delta or POC reference errors")
                
                # Log recent error patterns if available
                if hasattr(stream, 'get_recent_errors'):
                    recent_errors = stream.get_recent_errors()
                    if recent_errors:
                        hevc_errors = [err for err in recent_errors if 'cu_qp_delta' in str(err.get('error', '')) or 'Could not find ref with POC' in str(err.get('error', ''))]
                        if hevc_errors:
                            logging.warning(f"   🔥 Recent HEVC errors detected: {len(hevc_errors)} codec-related errors")
                            self.hevc_error_count += len(hevc_errors)
                            
                            # Log sample of recent HEVC errors for debugging
                            for i, err in enumerate(hevc_errors[-3:]):  # Show last 3 errors
                                logging.warning(f"   🔥 HEVC Error {i+1}: {err.get('error', '')[:100]}...")
            else:
                logging.info(f"📊 Stream {worker_source_id} not found in regular streams, checking direct device streams...")
                
        except Exception as e:
            logging.error(f"Error getting stream diagnostics: {e}")

    def _should_attempt_hevc_recovery(self, video_manager, worker_source_id) -> bool:
        """
        Determine if HEVC recovery should be attempted based on error patterns and cooldown.
        """
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self.last_hevc_recovery < self.hevc_recovery_cooldown:
            logging.debug(f"HEVC recovery on cooldown ({current_time - self.last_hevc_recovery:.1f}s elapsed)")
            return False
        
        # Check if stream has HEVC-related errors
        if hasattr(video_manager, 'streams') and worker_source_id in video_manager.streams:
            stream = video_manager.streams[worker_source_id]
            if hasattr(stream, 'get_recent_errors'):
                recent_errors = stream.get_recent_errors(max_age_seconds=60)  # Last minute
                hevc_errors = [err for err in recent_errors if 
                             'cu_qp_delta' in str(err.get('error', '')) or 
                             'Could not find ref with POC' in str(err.get('error', ''))]
                
                if len(hevc_errors) >= 3:  # Threshold for HEVC errors
                    logging.info(f"HEVC recovery warranted: {len(hevc_errors)} HEVC errors in last minute")
                    return True
        
        # Check if we have accumulated enough general HEVC errors
        if self.hevc_error_count >= 5:
            logging.info(f"HEVC recovery warranted: {self.hevc_error_count} total HEVC errors detected")
            return True
        
        return False

    def _handle_hevc_recovery(self, video_manager, worker_source_id):
        """
        Handle HEVC-specific recovery strategies for codec errors.
        This method attempts to recover from common HEVC issues like QP delta and POC reference errors.
        """
        try:
            self.last_hevc_recovery = time.time()  # Update recovery timestamp
            logging.info(f"🔧 Attempting HEVC stream recovery for {worker_source_id}")
            
            # Get the stream URL for recreation
            stream_url = video_manager.get_stream_url(worker_source_id)
            if not stream_url:
                logging.error(f"   Cannot get stream URL for {worker_source_id}")
                return False
            
            # Strategy 1: Remove and re-add the stream to reset decoder state
            logging.info(f"   Recreating stream {worker_source_id} to reset decoder state...")
            video_manager.remove_stream(worker_source_id)
            time.sleep(1.0)  # Give time for cleanup
            
            # Re-add the stream
            video_manager.add_stream(worker_source_id, stream_url)
            time.sleep(2.0)  # Give time for stream to initialize
            
            # Strategy 2: Check if stream was successfully recreated
            if not video_manager.has_stream(worker_source_id):
                logging.error(f"   Failed to recreate stream {worker_source_id}")
                return False
            
            # Strategy 3: Reset failure counters and error counts after recovery attempt
            self.reset_frame_failure_counters()
            self.hevc_error_count = 0  # Reset HEVC error counter
            
            logging.info(f"✅ HEVC recovery attempt completed for {worker_source_id}")
            return True
            
        except Exception as e:
            logging.error(f"❌ HEVC recovery failed for {worker_source_id}: {e}")
            return False

    def stop(self):
        """Stops the Pipeline processor and cleans up resources."""
        if not self.running:  # Prevent multiple stops
            return
            
        logging.info("🛑 Stopping PipelineProcessor...")
        self.running = False

        # Stop RTMP streamer first
        if hasattr(self, 'rtmp_streamer') and self.rtmp_streamer:
            try:
                self.rtmp_streamer.stop_stream()
                self.rtmp_streamer = None
            except Exception as e:
                logging.error(f"Error stopping RTMP streamer: {e}")

        # Clear frame queue before joining thread
        try:
            while True:
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break
        except Exception as e:
            logging.error(f"Error clearing frame queue: {e}")

        # Wait for detection thread with increased timeout
        if self.detection_thread and self.detection_thread.is_alive():
            try:
                self.detection_thread.join(timeout=5.0)  # Increased timeout
                if self.detection_thread.is_alive():
                    logging.warning("Detection thread did not terminate cleanly")
            except Exception as e:
                logging.error(f"Error joining detection thread: {e}")
            finally:
                self.detection_thread = None

        # Clear tracked objects
        self.tracked_objects_render.clear()  # Use clear() instead of reassignment

        # Close video debugger windows last
        try:
            if hasattr(self, 'video_debugger'):
                self.video_debugger.close_all()
        except Exception as e:
            logging.error(f"Error closing video debugger: {e}")

        logging.info("✅ PipelineProcessor stopped successfully")
        
    def _get_detection_interval(self):
        """
        Get detection interval from configuration.
        Converts frames per second to seconds per frame.
        """
        config = self.config_manager.get_feature_config("processing_speed")
        fps = config.get("decimal", 1.0)
        
        if fps <= 0:
            return 1 / 10  # Default to 10 frame per second if fps is zero or negative 
        
        return 1.0 / fps  # Convert fps to seconds per frame

    def enable_debug(self):
        """Enable debug mode for this pipeline."""
        self.debug_flag = True
        # Reset failure counters when debug is enabled as it may help with recovery
        self.consecutive_frame_failures = 0
        self.last_successful_frame_time = time.time()
    
    def reset_frame_failure_counters(self):
        """Reset frame failure counters. Can be called externally to help with recovery."""
        logging.info(f"🔄 Resetting frame failure counters for pipeline {self.pipeline_id}")
        self.consecutive_frame_failures = 0
        self.last_successful_frame_time = time.time()
        self.hevc_error_count = 0  # Also reset HEVC error count
    
    def get_hevc_diagnostics(self, video_manager) -> dict:
        """Get HEVC-specific diagnostics for the pipeline."""
        diagnostics = {
            'hevc_error_count': self.hevc_error_count,
            'last_hevc_recovery': self.last_hevc_recovery,
            'time_since_last_recovery': time.time() - self.last_hevc_recovery,
            'recovery_cooldown_remaining': max(0, self.hevc_recovery_cooldown - (time.time() - self.last_hevc_recovery)),
            'consecutive_failures': self.consecutive_frame_failures,
            'time_since_last_frame': time.time() - self.last_successful_frame_time,
        }
        
        # Add stream-specific HEVC information
        if hasattr(video_manager, 'streams') and self.worker_source_id in video_manager.streams:
            stream = video_manager.streams[self.worker_source_id]
            
            if hasattr(stream, 'get_codec_info'):
                diagnostics['codec'] = stream.get_codec_info()
                
            if hasattr(stream, 'get_recent_errors'):
                recent_errors = stream.get_recent_errors(max_age_seconds=300)  # Last 5 minutes
                hevc_errors = [err for err in recent_errors if 
                             'cu_qp_delta' in str(err.get('error', '')) or 
                             'Could not find ref with POC' in str(err.get('error', ''))]
                diagnostics['recent_hevc_errors'] = len(hevc_errors)
                diagnostics['total_recent_errors'] = len(recent_errors)
        
        return diagnostics