from typing import Any, Dict, List, Tuple

import numpy as np
from ...ai.FrameDrawer import FrameDrawer
from .DetectionProcessor import DetectionProcessor
from ...pipeline.PipelineConfigManager import PipelineConfigManager
from ...repositories.PPEDetectionRepository import PPEDetectionRepository
from ...util.PersonAttributeMatcher import PersonAttributeMatcher
from ...callbacks import DetectionType, DetectionAttribute, BoundingBox, DetectionData

class PPEDetectionProcessor(DetectionProcessor):
    code = "ppe"
    icons = {
        "helmet": "icons/helmet-green.png",
        "no_helmet": "icons/helmet-red.png",
        "vest": "icons/vest-green.png",
        "no_vest": "icons/vest-red.png"
    }
    
    def __init__(self):
        self.ppe_storage = PPEDetectionRepository()
        self.types = []
        self.ppe_groups = {}
        self.group_thresholds = {}
        self.main_class_threshold = 0.7
        self.main_class = "person"
        
        self.labels = ["helmet", "no_helmet", "vest", "no_vest", "gloves", "no_gloves", "goggles", "no_goggles", "boots", "no_boots"]
        self.violation_labels = ["no_helmet", "no_vest", "no_gloves", "no_goggles", "no_boots"]
        self.compliance_labels = ["helmet", "vest", "gloves", "goggles", "boots"]
        self.exclusive_labels = [("helmet", "no_helmet"), ("vest", "no_vest"), ("gloves", "no_gloves"), ("goggles", "no_goggles"), ("boots", "no_boots")]

    def update(self, config_manager: PipelineConfigManager, ai_model=None):
        config = config_manager.get_feature_config(self.code, {})
        
        # Update from AI model
        if ai_model:
            self._update_from_ai_model(ai_model)
        
        # Update PPE type configuration
        ppe_type_configs = config.get("ppeType", [])
        self.types = []
        self.group_thresholds = {}
        
        for ppe_config in ppe_type_configs:
            if isinstance(ppe_config, dict):
                group = ppe_config.get("group")
                threshold = ppe_config.get("confidenceThreshold", 0.7)
                if group:
                    self.types.append(group)
                    self.group_thresholds[group] = threshold
            elif isinstance(ppe_config, str):
                # Backward compatibility
                self.types.append(ppe_config)
                self.group_thresholds[ppe_config] = 0.7
        
        # Update main class threshold
        self.main_class_threshold = config.get("mainClassConfidenceThreshold", 0.7)

    def _update_from_ai_model(self, ai_model):
        """Update processor settings from AI model configuration"""
        if ai_model and hasattr(ai_model, 'ppe_groups') and ai_model.ppe_groups:
            self.ppe_groups = {group.group_name: group for group in ai_model.ppe_groups}
            self._build_labels_from_groups()
            
        if ai_model and hasattr(ai_model, 'main_class') and ai_model.main_class:
            self.main_class = ai_model.main_class

    def _build_labels_from_groups(self):
        """Build standard PPE labels from AI model PPE groups"""
        if not self.ppe_groups:
            return
            
        labels = []
        violation_labels = []
        compliance_labels = []
        exclusive_labels = []
        
        for group_name in self.ppe_groups.items():
            compliance_class = group_name  
            violation_class = f"no_{group_name}" 
            
            # Build label lists using standard naming
            labels.extend([compliance_class, violation_class])
            compliance_labels.append(compliance_class)
            violation_labels.append(violation_class)
            exclusive_labels.append((compliance_class, violation_class))
        
        # Update instance variables with dynamic labels
        self.labels = labels
        self.violation_labels = violation_labels
        self.compliance_labels = compliance_labels
        self.exclusive_labels = exclusive_labels

    def get_multi_instance_classes(self):
        """Get PPE classes that can have multiple instances per person"""
        multi_instance_base = ["boots", "gloves", "goggles"]
        multi_instance = []
        
        for label in self.labels:
            base_label = label.replace("no_", "") if label.startswith("no_") else label
            if base_label in multi_instance_base:
                multi_instance.append(label)
        return multi_instance

    def process(self, detections: List[Dict[str, Any]], dimension: Tuple[int, int]) -> List[Dict[str, Any]]:
        persons = [d for d in detections if d["label"] == self.main_class]
        
        ppe_attributes = []
        for detection in detections:
            label = detection["label"]
            
            for group_name in self.types:
                if group_name in self.ppe_groups:
                    group_config = self.ppe_groups[group_name]
                    
                    original_compliance = group_config.get("compliance")
                    original_violation = group_config.get("violation")
                    
                    if label in [original_compliance, original_violation]:
                        if label == original_compliance:
                            detection["label"] = group_name
                        elif label == original_violation:
                            detection["label"] = f"no_{group_name}"
                        
                        ppe_attributes.append(detection)
                        break
                elif label == group_name or label == f"no_{group_name}":
                    ppe_attributes.append(detection)
                    break

        matched_results = PersonAttributeMatcher.match_persons_with_attributes(
            persons, ppe_attributes, coverage_threshold=0.5
        )

        return matched_results

    def get_class_thresholds(self):
        """Get confidence thresholds for each class using original AI model class names"""
        thresholds = {}
        
        for group_name, threshold in self.group_thresholds.items():
            if group_name in self.ppe_groups:
                group_config = self.ppe_groups[group_name]
                
                original_compliance = group_config.get("compliance")
                original_violation = group_config.get("violation")
                
                if original_compliance:
                    thresholds[original_compliance] = threshold
                if original_violation:
                    thresholds[original_violation] = threshold
                    
                thresholds[group_name] = threshold
                thresholds[f"no_{group_name}"] = threshold
            else:
                thresholds[group_name] = threshold
                if not group_name.startswith("no_"):
                    thresholds[f"no_{group_name}"] = threshold
        
        return thresholds

    def save_to_db(self, pipeline_id: str, worker_source_id: str, frame_counter: int, tracked_objects: List[Dict[str, Any]], frame: np.ndarray, frame_drawer: FrameDrawer):
        self.ppe_storage.save_ppe_detection(
            pipeline_id, worker_source_id, frame_counter, tracked_objects, frame, frame_drawer
        )

    @staticmethod
    def create_detection_data(pipeline_id: str, worker_source_id: str, person_id: str, 
                                    detection_id: str, tracked_obj: Dict[str, Any], 
                                    image_path: str = "", image_tile_path: str = "",
                                    frame_id: int = 0) -> DetectionData:
        """Create DetectionData from PPE detection data."""
        bbox = BoundingBox.from_list(tracked_obj["bbox"])
        
        attributes = []
        for attr in tracked_obj.get("attributes", []):
            attr_bbox = None
            if "bbox" in attr:
                attr_bbox = BoundingBox.from_list(attr["bbox"])
            
            # Determine if this is a violation based on label
            is_violation = attr["label"].startswith("no_") or attr["label"] in [
                "no_helmet", "no_vest", "no_gloves", "no_goggles", "no_boots"
            ]
            
            attributes.append(DetectionAttribute(
                label=attr["label"],
                confidence=attr.get("confidence", 1.0),
                count=attr.get("count", 0),
                bbox=attr_bbox,
                is_violation=is_violation
            ))
        
        return DetectionData(
            detection_type=DetectionType.PPE_DETECTION,
            detection_id=detection_id,
            person_id=person_id,
            pipeline_id=pipeline_id,
            worker_source_id=worker_source_id,
            confidence_score=tracked_obj.get("confidence", 1.0),
            bbox=bbox,
            attributes=attributes,
            image_path=image_path,
            image_tile_path=image_tile_path,
            frame_id=frame_id
        )
