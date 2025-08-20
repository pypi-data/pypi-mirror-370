from abc import ABC, abstractmethod

class BaseDetector(ABC):
    """
    Abstract base class for all object detectors.
    """

    @abstractmethod
    def load_model(self, model_metadata):
        pass

    @abstractmethod
    def detect_objects(self, frame, confidence_threshold=0.7, class_thresholds=None):
        """
        Detect objects in the input frame.
        Args:
            frame: Image/frame (numpy array)
            confidence_threshold: Minimum confidence threshold for detections (optional)
            class_thresholds: Dict mapping class names to specific confidence thresholds (optional)
        Returns:
            List of detections: [{"label": str, "confidence": float, "bbox": [x1, y1, x2, y2]}, ...]
        """
        pass
