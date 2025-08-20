from typing import Any, Dict, List, Tuple

import numpy as np
from shapely.geometry import Polygon
from .DetectionProcessor import DetectionProcessor
from ...pipeline.PipelineConfigManager import PipelineConfigManager
from ...repositories.RestrictedAreaRepository import RestrictedAreaRepository
from ...util.PersonRestrictedAreaMatcher import PersonRestrictedAreaMatcher
from ...callbacks import DetectionType, DetectionAttribute, BoundingBox, DetectionData


class HumanDetectionProcessor(DetectionProcessor):
    code = "human"
    labels = ["in_restricted_area"]
    violation_labels = ["in_restricted_area"]

    def __init__(self):
        self.repository = RestrictedAreaRepository()
        self.restricted_areas = []
        self.main_class_threshold = 0.7
        self.main_class = "person"  # Default fallback

    def update(self, config_manager: PipelineConfigManager, ai_model=None):
        config = config_manager.get_feature_config(self.code, {})
        area_list = config.get("restrictedArea", [])
        self.restricted_areas = [
            [(p["x"], p["y"]) for p in area] for area in area_list
        ]
        
        # Update main class threshold
        self.main_class_threshold = config.get("minimumDetectionConfidence", 0.7)
        
        # Update main class from AI model
        if ai_model and ai_model.get_main_class():
            self.main_class = ai_model.get_main_class()
        else:
            self.main_class = "person"  # Default fallback

    def get_main_class_threshold(self, ai_model=None):
        """Get the confidence threshold for the main class (person)"""
        if ai_model and ai_model.get_main_class():
            return self.main_class_threshold
        return None

    def process(self, detections: List[Dict[str, Any]], dimension: Tuple[int, int]) -> List[Dict[str, Any]]:
        persons = [d for d in detections if d["label"] == self.main_class]

        height, width = dimension
        area_polygons = []

        for area in self.restricted_areas:
            points = [(int(x * width), int(y * height)) for x, y in area]
            area_polygons.append(Polygon(points))

        matched_results = PersonRestrictedAreaMatcher.match_persons_with_restricted_areas(
            persons, area_polygons
        )

        return matched_results

    def save_to_db(self, pipeline_id: str, worker_source_id: str, frame_counter: int, tracked_objects: List[Dict[str, Any]], frame: np.ndarray, frame_drawer):
        """Save the processed detections to the database if the feature is enabled."""
        self.repository.save_area_violation(
            pipeline_id, worker_source_id, frame_counter, tracked_objects, frame, frame_drawer
        )

    def get_multi_instance_classes(self):
        """Human detection doesn't have multi-instance classes"""
        return []

    @staticmethod
    def create_detection_data(pipeline_id: str, worker_source_id: str, person_id: str,
                                    detection_id: str, tracked_obj: Dict[str, Any],
                                    image_path: str = "", image_tile_path: str = "",
                                    frame_id: int = 0) -> DetectionData:
        """Create DetectionData from area violation data."""
        bbox = BoundingBox.from_list(tracked_obj["bbox"])
        
        attributes = []
        for attr in tracked_obj.get("attributes", []):
            # Area violations are always violations
            attributes.append(DetectionAttribute(
                label=attr["label"],
                confidence=attr.get("confidence", 1.0),
                count=attr.get("count", 0),
                is_violation=True
            ))
        
        return DetectionData(
            detection_type=DetectionType.AREA_VIOLATION,
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
