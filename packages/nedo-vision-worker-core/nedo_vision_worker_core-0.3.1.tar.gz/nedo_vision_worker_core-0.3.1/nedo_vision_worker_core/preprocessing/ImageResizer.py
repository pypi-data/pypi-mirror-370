from typing import Tuple
import cv2
import numpy as np
from ..pipeline.PipelineConfigManager import PipelineConfigManager
from .Preprocessor import Preprocessor


class ImageResizer(Preprocessor):
    def __init__(self):
        self.code = "resize"
        self.is_enabled = False
        self.factor = 1.0

    def _get_factor(self, config: PipelineConfigManager) -> float:
        if not self.is_enabled:
            return 1.0
        
        resize_factor = config.get_feature_config(self.code, "1")

        try:
            return float(resize_factor)
        except (ValueError, TypeError):
            return 1.0

    def update_config(self, config: PipelineConfigManager):
        self.is_enabled = config.is_feature_enabled(self.code)
        self.factor = self._get_factor(config)

    def apply(self, image: np.ndarray) -> np.ndarray:
        if not self.is_enabled or self.factor == 1.0:
            return image

        height, width = image.shape[:2]
        new_height, new_width = int(height / self.factor), int(width / self.factor)

        return cv2.resize(image, (new_width, new_height))
    
    def revert_bboxes(self, bboxes: np.ndarray, dimension: Tuple[int, int]) -> np.ndarray:
        if not self.is_enabled or self.factor == 1.0:
            return bboxes

        return bboxes * self.factor