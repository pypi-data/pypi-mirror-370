from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

import numpy as np

from ...ai.FrameDrawer import FrameDrawer
from ...pipeline.PipelineConfigManager import PipelineConfigManager

class DetectionProcessor(ABC):
    code = ""
    icons = {}
    labels = []
    exclusive_labels = []
    violation_labels = []
    compliance_labels = []

    @abstractmethod
    def process(self, detections: List[Dict[str, Any]], dimension: Tuple[int, int]) -> List[Dict[str, Any]]:
        """Process raw detections and return processed results."""
        pass

    @abstractmethod
    def update(self, config_manager: PipelineConfigManager, ai_model=None):
        pass

    @abstractmethod
    def save_to_db(self, pipeline_id: str, worker_source_id: str, frame_counter: int, tracked_objects: List[Dict[str, Any]], frame: np.ndarray, frame_drawer: FrameDrawer):
        """Save processed detections to the database."""
        pass
