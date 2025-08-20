import cv2
import logging
from ultralytics import YOLO
from ..database.DatabaseManager import DatabaseManager
from .BaseDetector import BaseDetector
from ..models.ai_model import AIModelEntity

logging.getLogger("ultralytics").setLevel(logging.WARNING)

class YOLODetector(BaseDetector):
    def __init__(self, model: AIModelEntity):
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
        
        # Check if file exists and has content
        if not path.is_file() or path.stat().st_size == 0:
            logging.error(f"❌ Model file not found or empty: {path}")
            self.model = None
            return False
            
        try:
            self.model = YOLO(path)
            return True
        except Exception as e:
            logging.error(f"❌ Error loading YOLO model {model.name}: {e}")
            self.model = None
            return False

    def detect_objects(self, frame, confidence_threshold=0.7, class_thresholds=None):
        if self.model is None:
            return []

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model(frame_rgb)

        class_names = self.metadata.get_classes()
        if not class_names:
            class_names = self.model.names

        detections = []
        for box in results[0].boxes:
            class_id = int(box.cls)
            label = class_names[class_id]
            confidence = float(box.conf)

            threshold = confidence_threshold
            if class_thresholds and label in class_thresholds:
                threshold = class_thresholds[label]

            if confidence < threshold:
                continue

            detections.append({
                "label": label,
                "confidence": confidence,
                "bbox": box.xyxy.tolist()[0]
            })

        return detections
