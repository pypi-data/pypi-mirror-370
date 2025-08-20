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
                    logging.warning(f"⚠️ No frame available for {worker_source_id}. Retrying...")
                    # Check if stream was removed
                    if not video_manager.has_stream(worker_source_id):
                        logging.info(f"🛑 Stream {worker_source_id} was removed, stopping pipeline")
                        break
                    time.sleep(0.01)
                    continue

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
        for retry_count in range(max_retries):
            frame = video_manager.get_frame(self.worker_source_id)
            if frame is not None:
                return frame
            logging.warning(f"⚠️ Waiting for video stream {self.worker_source_id} (Attempt {retry_count + 1}/{max_retries})...")
            time.sleep(sleep_time)

        return None

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