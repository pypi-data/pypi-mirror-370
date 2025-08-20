import logging
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
from .BaseDetector import BaseDetector
from .RFDETRDetector import RFDETRDetector
from .YOLODetector import YOLODetector


class DetectionManager:
    def __init__(self, model=None):
        self.detector: BaseDetector | None = None
        self.model_metadata = None

        if model:
            self.load_model(model)

    def load_model(self, model):
        """
        Loads a new model at runtime and replaces current detector if successful.
        Checks download status before attempting to load the model.
        """
        if not model:
            if self.detector:
                logging.info("🧹 Model unloaded")
            self.detector = None
            self.model_metadata = None
            return

        # Check download status before loading
        if not model.is_ready_for_use():
            if model.is_downloading():
                logging.warning(f"⏳ Model {model.name} is still downloading. Skipping load.")
                self.detector = None
                self.model_metadata = None
                return
            elif model.has_download_failed():
                logging.error(f"❌ Model {model.name} download failed: {model.download_error}")
                self.detector = None
                self.model_metadata = None
                return
            else:
                logging.warning(f"⚠️ Model {model.name} is not ready for use (status: {model.download_status})")
                self.detector = None
                self.model_metadata = None
                return

        detector_type = model.type.lower()

        try:
            if detector_type == "yolo":
                detector = YOLODetector(model)
            elif detector_type == "rf_detr":
                detector = RFDETRDetector(model)
            else:
                raise ValueError(f"Unsupported model type: {detector_type}")

            if detector.model is not None:
                self.detector = detector
                self.model_metadata = model
                # Log device info
                if TORCH_AVAILABLE:
                    device = "GPU" if torch.cuda.is_available() else "CPU"
                else:
                    device = "CPU (torch not installed)"
                logging.info(f"🚀 Model {model.name} loaded on {device}")
                logging.info(f"📥 Model {model.name} with {detector_type} detector loaded")
            else:
                logging.error(f"❌ Error loading model: {model.name} with {detector_type} detector")
                self.detector = None
                self.model_metadata = None

        except Exception as e:
            logging.error(f"❌ Error loading model: {model.name} with {detector_type} detector: {e}")
            self.detector = None
            self.model_metadata = None

    def detect_objects(self, frame, confidence_threshold=0.7, class_thresholds=None):
        if not self.detector:
            return []
        return self.detector.detect_objects(frame, confidence_threshold, class_thresholds)
