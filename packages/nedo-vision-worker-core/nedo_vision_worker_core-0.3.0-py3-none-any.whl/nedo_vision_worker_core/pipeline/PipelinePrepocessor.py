from typing import List, Tuple
import numpy as np
from .PipelineConfigManager import PipelineConfigManager
from ..preprocessing.ImageResizer import ImageResizer
from ..preprocessing.ImageRoi import ImageRoi
from ..preprocessing.Preprocessor import Preprocessor


class PipelinePrepocessor:
    def __init__(self):
        self.preprocessors: List[Preprocessor] = [
            ImageRoi(),
            ImageResizer()
        ]

    def update(self, config: PipelineConfigManager):
        for preprocessor in self.preprocessors:
            preprocessor.update_config(config)
    
    def apply(self, image: np.ndarray) -> np.ndarray:
        image = image.copy()

        for preprocessor in self.preprocessors:
            image = preprocessor.apply(image)

        return image
    
    def revert_detections_bboxes(self, detections: list, dimension: Tuple[int, int]) -> np.ndarray:
        if not detections or len(detections) < 1:
            return detections
        
        bboxes = np.array([det["bbox"] for det in detections])

        for preprocessor in reversed(self.preprocessors):
            bboxes = preprocessor.revert_bboxes(bboxes, dimension)

        for det, bbox in zip(detections, bboxes):
            det["bbox"] = bbox

        return detections