import json
import logging
import time
import threading
from typing import Dict, Set, Optional, Callable
from ..repositories.AIModelRepository import AIModelRepository
from ..repositories.WorkerSourcePipelineDebugRepository import WorkerSourcePipelineDebugRepository
from ..repositories.WorkerSourcePipelineRepository import WorkerSourcePipelineRepository
from .PipelineManager import PipelineManager
from ..streams.VideoStreamManager import VideoStreamManager
from ..util.ModelReadinessChecker import ModelReadinessChecker


class PipelineSyncThread(threading.Thread):
    """Thread responsible for synchronizing worker source pipelines from the database in real-time."""

    def __init__(self, video_manager: VideoStreamManager, polling_interval=5, max_workers=4):
        super().__init__(daemon=True)  # Runs as a daemon
        self.video_manager = video_manager
        self.polling_interval = polling_interval
        self.pipeline_repo = WorkerSourcePipelineRepository()
        self.debug_repo = WorkerSourcePipelineDebugRepository()
        self.ai_model_repo = AIModelRepository()
        self.running = True
        self.pipeline_manager = PipelineManager(video_manager, self.on_pipeline_stopped, max_workers)

    def _parse_json(self, value: str) -> Optional[dict]:
        """Attempts to parse the value as JSON if applicable."""
        if not value:
            return None
        
        value = value.strip()  # Remove leading/trailing spaces
        if (value.startswith("{") and value.endswith("}")) or (value.startswith("[") and value.endswith("]")):
            try:
                return json.loads(value)  # Parse JSON object or list
            except json.JSONDecodeError:
                pass  # Keep as string if parsing fails
        return None
        
    def on_pipeline_stopped(self, pipeline_id: str) -> None:
        """Set the pipeline as stopped in the database."""
        pipeline = self.pipeline_repo.get_worker_source_pipeline(pipeline_id)
        pipeline.pipeline_status_code = "run" if pipeline.pipeline_status_code == "restart" else "stop"
        self.pipeline_repo.session.commit()

    def run(self) -> None:
        """Continuously updates pipelines based on database changes."""
        while self.running:
            try:
                # Cache model and pipeline data
                models = {m.id: m for m in self.ai_model_repo.get_models()}
                db_pipelines = {p.id: p for p in self.pipeline_repo.get_all_pipelines()}
                
                # Get pipeline IDs for comparison
                local_pipeline_ids = set(self.pipeline_manager.get_active_pipelines())
                db_pipeline_ids = set(db_pipelines.keys())

                restarted_pipeline = False

                # Helper function for model lookup
                def get_model(pipeline):
                    return models.get(pipeline.ai_model_id)

                # Process pipeline changes
                self._add_new_pipelines(db_pipeline_ids - local_pipeline_ids, db_pipelines, get_model, restarted_pipeline)
                self._remove_deleted_pipelines(local_pipeline_ids - db_pipeline_ids)
                self._update_existing_pipelines(db_pipeline_ids & local_pipeline_ids, db_pipelines, get_model)

                if restarted_pipeline:
                    self.pipeline_repo.session.commit()

            except Exception as e:
                logging.error(f"⚠️ Error syncing pipelines from database: {e}", exc_info=True)

            time.sleep(self.polling_interval) 

    def _add_new_pipelines(self, pipeline_ids: Set[str], db_pipelines: Dict[str, object], 
                           get_model: Callable, restarted_pipeline: bool) -> None:
        """Add new pipelines that exist in DB but not locally."""
        for pid in pipeline_ids:
            pipeline = db_pipelines[pid]

            if pipeline.pipeline_status_code == 'restart':
                pipeline.pipeline_status_code = 'run'
                restarted_pipeline = True

            if pipeline.pipeline_status_code == 'run':
                model = get_model(pipeline)
                
                # Check if model is ready before starting pipeline
                if model:
                    readiness = ModelReadinessChecker.check_model_readiness(model)
                    if not readiness["ready"]:
                        logging.warning(f"⚠️ Pipeline {pid} ({pipeline.name}): {readiness['reason']}. Skipping pipeline start.")
                        continue
                
                logging.info(f"🟢 Adding new pipeline: {pid} ({pipeline.name})")
                self.pipeline_manager.start_pipeline(pipeline, model)

    def _remove_deleted_pipelines(self, pipeline_ids: Set[str]) -> None:
        """Remove pipelines that exist locally but not in DB."""
        for pid in pipeline_ids:
            logging.info(f"🔴 Removing deleted pipeline: {pid}")
            self.pipeline_manager.stop_pipeline(pid)

    def _update_existing_pipelines(self, pipeline_ids: Set[str], db_pipelines: Dict[str, object], 
                                  get_model: Callable) -> None:
        """Update existing pipelines that need changes."""
        debug_pipeline_ids = self.debug_repo.get_pipeline_ids_to_debug()

        for pid in pipeline_ids:
            db_pipeline = db_pipelines[pid]
            local_pipeline = self.pipeline_manager.get_pipeline(pid)
            processor = self.pipeline_manager.processors[pid]
            local_proc = processor.detection_manager
            db_model = get_model(db_pipeline)

            self.update_pipeline(pid, db_pipeline, local_pipeline, local_proc, db_model, local_proc.model_metadata)
            if pid in debug_pipeline_ids:
                processor.enable_debug()

    def update_pipeline(self, pid, db_pipeline, local_pipeline, local_proc, db_model, local_model):
        """Handles pipeline updates, ensuring correct model and status."""
        processor = self.pipeline_manager.processors.get(pid)
        processor.frame_drawer.location_name = db_pipeline.location_name

        # Case 1: Pipeline should be running but isn't
        if db_pipeline.pipeline_status_code == "run" and not self.pipeline_manager.is_running(pid):
            logging.info(f"🟢 Starting pipeline {pid}: {db_pipeline.name} (status: RUNNING)")
            self.pipeline_manager.start_pipeline(db_pipeline, db_model)

        # Case 2: Pipeline should be stopped but is running
        elif db_pipeline.pipeline_status_code == "stop" and self.pipeline_manager.is_running(pid):
            logging.info(f"🔴 Stopping pipeline {pid}: {db_pipeline.name} (status: STOPPED)")
            self.pipeline_manager.stop_pipeline(pid)

        # Case 3: Pipeline configuration has changed, needs restart
        elif self._has_pipeline_changed(local_pipeline, db_pipeline):
            logging.info(f"🟡 Updating pipeline {pid}: {db_pipeline.name} (status: RESTARTING)")
            if self.pipeline_manager.is_running(pid):
                self.pipeline_manager.stop_pipeline(pid)
            self.pipeline_manager.start_pipeline(db_pipeline, db_model)

        # Case 4: AI Model has changed
        elif local_model and db_model and local_model.id != db_model.id:
            if db_model:
                readiness = ModelReadinessChecker.check_model_readiness(db_model)
                if readiness["ready"]:
                    local_proc.load_model(db_model)
                    logging.info(f"🔄 Model updated for pipeline {pid}: {db_pipeline.name} "
                                 f"(version: {db_model.version if db_model else 'removed'})")
                else:
                    logging.warning(f"⚠️ Pipeline {pid}: {readiness['reason']}")

        # Case 5: Local model exists but doesn't match DB model
        elif local_model and (not db_model or local_model.version != db_model.version):
            if not db_model or ModelReadinessChecker.check_model_readiness(db_model)["ready"]:
                local_proc.load_model(db_model)
                logging.info(f"🔄 Model updated for pipeline {pid}: {db_pipeline.name} "
                             f"(version: {db_model.version if db_model else 'removed'})")
            else:
                readiness = ModelReadinessChecker.check_model_readiness(db_model)
                logging.warning(f"⚠️ Pipeline {pid}: {readiness['reason']}")

        # Case 6: DB model exists but local model doesn't
        elif db_model and not local_model:
            readiness = ModelReadinessChecker.check_model_readiness(db_model)
            if readiness["ready"]:
                logging.info(f"🔄 Added model for pipeline {pid}: {db_pipeline.name} (version: {db_model.version})")
                local_proc.load_model(db_model)
            else:
                logging.warning(f"⚠️ Pipeline {pid}: {readiness['reason']}")

        # Case 7: Model metadata has changed (same ID and version, but different properties)
        elif local_model and db_model and local_model.id == db_model.id and local_model.version == db_model.version:
            # Check if model metadata (classes, PPE groups, main_class) has changed
            if self._has_model_metadata_changed(local_model, db_model):
                readiness = ModelReadinessChecker.check_model_readiness(db_model)
                if readiness["ready"]:
                    local_proc.load_model(db_model)
                    logging.info(f"🔄 Model metadata updated for pipeline {pid}: {db_pipeline.name} "
                                 f"(same version {db_model.version}, updated properties)")
                else:
                    logging.warning(f"⚠️ Pipeline {pid}: {readiness['reason']}")

    def _has_model_metadata_changed(self, local_model, db_model):
        """Check if model metadata has changed without version change."""
        # Compare classes
        local_classes = set(local_model.get_classes() or [])
        db_classes = set(db_model.get_classes() or [])
        if local_classes != db_classes:
            return True
        
        # Compare PPE class groups
        local_ppe_groups = local_model.get_ppe_class_groups() or {}
        db_ppe_groups = db_model.get_ppe_class_groups() or {}
        if local_ppe_groups != db_ppe_groups:
            return True
        
        # Compare main class
        if local_model.get_main_class() != db_model.get_main_class():
            return True
        
        return False

    def _has_pipeline_changed(self, local_pipeline, db_pipeline):
        """Checks if the pipeline configuration has changed."""
        if db_pipeline.pipeline_status_code == "restart":
            return True

        local_configs = local_pipeline.worker_source_pipeline_configs
        db_configs = db_pipeline.worker_source_pipeline_configs

        # Convert config objects to comparable structures
        local_config_values = [
            (config.pipeline_config_id, config.is_enabled, config.value, 
             config.pipeline_config_name, config.pipeline_config_code)
            for config in local_configs
        ]

        db_config_values = [
            (config.pipeline_config_id, config.is_enabled, config.value, 
             config.pipeline_config_name, config.pipeline_config_code)
            for config in db_configs
        ]

        return sorted(local_config_values) != sorted(db_config_values)

    def stop(self):
        """Stops the synchronization thread and shuts down pipelines properly."""
        logging.info("🛑 Stopping PipelineSyncThread...")
        self.running = False
        self.video_manager.stop_all()
        self.pipeline_manager.shutdown()