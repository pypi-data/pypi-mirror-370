import cv2
import logging
try:
    from rfdetr import RFDETRBase
    RFDETR_AVAILABLE = True
except ImportError:
    RFDETR_AVAILABLE = False
    RFDETRBase = None

from ..database.DatabaseManager import DatabaseManager
from ..models.ai_model import AIModelEntity
from .BaseDetector import BaseDetector

logging.getLogger("ultralytics").setLevel(logging.WARNING)

class RFDETRDetector(BaseDetector):
    def __init__(self, model: AIModelEntity):
        if not RFDETR_AVAILABLE:
            raise ImportError(
                "RF-DETR is required but not installed. Install it manually with:\n"
                "pip install rfdetr @ git+https://github.com/roboflow/rf-detr.git@1e63dbad402eea10f110e86013361d6b02ee0c09\n"
                "See the documentation for more details."
            )
        if not isinstance(model, AIModelEntity):
            raise TypeError("model must be an instance of AIModelEntity")
        self.model = None
        self.metadata = None

        if model:
            self.load_model(model)

    def load_model(self, model: AIModelEntity):
        if not isinstance(model, AIModelEntity):
            raise TypeError("model must be an instance of AIModelEntity")
        self.metadata = model
        path = DatabaseManager.STORAGE_PATHS["models"] / model.file
        
        if not path.is_file() or path.stat().st_size == 0:
            logging.error(f"❌ Model file not found or empty: {path}")
            self.model = None
            return False
            
        try:
            self.model = RFDETRBase(pretrain_weights=path.as_posix())
            self.model.optimize_for_inference()
            return True
        except Exception as e:
            logging.error(f"❌ Error loading RFDETR model {model.name}: {e}")
            self.model = None
            return False

    def detect_objects(self, frame, confidence_threshold=0.7, class_thresholds=None):
        if self.model is None:
            return []

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model.predict(frame_rgb, confidence_threshold)

        class_names = self.metadata.get_classes() if hasattr(self.metadata, "get_classes") else None
        if not class_names:
            class_names = getattr(self.model, "class_names", None)

        detections = []
        for class_id, conf, xyxy in zip(results.class_id, results.confidence, results.xyxy):
            label = class_names[class_id - 1] if class_names else str(class_id)
            
            threshold = confidence_threshold
            if class_thresholds and label in class_thresholds:
                threshold = class_thresholds[label]

            if conf < threshold:
                continue
                
            detections.append({
                "label": label,
                "confidence": conf,
                "bbox": xyxy
            })

        return detections
