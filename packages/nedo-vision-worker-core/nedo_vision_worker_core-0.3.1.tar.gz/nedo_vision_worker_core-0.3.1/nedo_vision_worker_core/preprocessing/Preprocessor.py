from abc import ABC, abstractmethod
from typing import Tuple
import numpy as np

from ..pipeline.PipelineConfigManager import PipelineConfigManager

class Preprocessor(ABC):
    @abstractmethod
    def update_config(self, config: PipelineConfigManager):
        pass
    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        pass
    @abstractmethod
    def revert_bboxes(self, bboxes: np.ndarray, dimension: Tuple[int, int]) -> np.ndarray:
        pass