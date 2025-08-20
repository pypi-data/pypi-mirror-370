import logging
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict
from .PipelineProcessor import PipelineProcessor
from ..streams.VideoStreamManager import VideoStreamManager

class PipelineManager:
    """Manages AI pipeline execution and video stream processing."""

    def __init__(self, video_manager: VideoStreamManager, on_pipeline_stopped, max_workers=50):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)  # Thread pool for parallel execution
        self.pipeline_threads = {}  # Stores Future objects {pipeline_id: Future}
        self.pipeline_metadata = {}  # Stores actual pipeline data {pipeline_id: metadata}
        self.video_manager = video_manager  # Manages video streams
        self.processors: Dict[str, PipelineProcessor] = {}  # Stores PipelineProcessor instances per pipeline
        self.running = True
        self._stopping_pipelines = set()  # Track pipelines being stopped
        self._stop_lock = threading.Lock()  # Lock for thread-safe pipeline stopping
        self.on_pipeline_stopped = on_pipeline_stopped

    def start_pipeline(self, pipeline, model):
        """
        Start a pipeline processing.
        Args:
            pipeline: The pipeline object (contains id, worker_source_id, name, etc.)
            model: The AI model to use for processing.
        """
        pipeline_id = pipeline.id
        worker_source_id = pipeline.worker_source_id

        if not self.running:
            logging.warning(f"⚠️ Attempt to start pipeline {pipeline_id} after shutdown.")
            return

        if self.is_running(pipeline_id):
            logging.warning(f"⚠️ Pipeline {pipeline_id} is already running.")
            return

        logging.info(f"🚀 Starting Pipeline processing for pipeline: {pipeline_id} | Source: {worker_source_id} ({pipeline.name})")

        processor = PipelineProcessor(pipeline_id, worker_source_id, model, False)
        processor.frame_drawer.location_name = pipeline.location_name
        self.processors[pipeline_id] = processor  # Store processor instance

        future = self.executor.submit(processor.process_pipeline, self.video_manager)
        self.pipeline_threads[pipeline_id] = future
        self.pipeline_metadata[pipeline_id] = pipeline

        # Add callback to detect when a pipeline finishes
        future.add_done_callback(lambda f: self._handle_pipeline_completion(pipeline_id, f))

    def _handle_pipeline_completion(self, pipeline_id: str, future: Future):
        """
        Handles cleanup when a pipeline finishes processing.
        """
        with self._stop_lock:
            if pipeline_id in self._stopping_pipelines:
                return  # If it's already being stopped manually, don't trigger again

        try:
            if future.cancelled():
                logging.info(f"🚫 Pipeline {pipeline_id} was cancelled.")
            elif future.exception():
                logging.error(f"❌ Pipeline {pipeline_id} encountered an error: {future.exception()}", exc_info=True)

        except Exception as e:
            logging.error(f"⚠️ Error in handling pipeline {pipeline_id} completion: {e}")

        finally:
            self.on_pipeline_stopped(pipeline_id)

    def stop_pipeline(self, pipeline_id: str):
        """Stop an AI processing pipeline."""
        with self._stop_lock:
            if pipeline_id in self._stopping_pipelines:
                logging.debug(f"Pipeline {pipeline_id} already being stopped, skipping")
                return
            self._stopping_pipelines.add(pipeline_id)

        try:
            # Stop AI processing
            processor = self.processors.pop(pipeline_id, None)
            if processor:
                processor.stop()

            # Cancel execution thread
            future = self.pipeline_threads.pop(pipeline_id, None)
            if future:
                future.cancel()

            # Remove metadata
            self.pipeline_metadata.pop(pipeline_id, None)

            logging.info(f"✅ Pipeline {pipeline_id} stopped successfully.")

        except Exception as e:
            logging.error(f"❌ Error during pipeline shutdown: {e}")
        
        finally:
            self._stopping_pipelines.discard(pipeline_id)
            self.on_pipeline_stopped(pipeline_id)

    def get_active_pipelines(self):
        """Returns a list of active pipeline IDs."""
        return list(self.pipeline_metadata.keys())

    def get_pipeline(self, pipeline_id):
        """Returns the actual pipeline metadata (not the Future object)."""
        return self.pipeline_metadata.get(pipeline_id, None)

    def is_running(self, pipeline_id):
        """
        Checks if a pipeline is currently running.
        
        Args:
            pipeline_id (str): The ID of the pipeline to check.
            
        Returns:
            bool: True if the pipeline is running, False otherwise.
        """
        return pipeline_id in self.pipeline_threads and not self.pipeline_threads[pipeline_id].done()

    def shutdown(self):
        """Shuts down the pipeline manager gracefully."""
        logging.info("🛑 Shutting down PipelineManager...")
        self.running = False

        for pipeline_id in list(self.pipeline_threads.keys()):
            self.stop_pipeline(pipeline_id)

        self.executor.shutdown(wait=True)  # Wait for all threads to finish
        logging.info("✅ PipelineManager stopped.")
