# repositories/restricted_area_repository.py

import os
import cv2
import datetime
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.restricted_area_violation import RestrictedAreaViolationEntity
from ..database.DatabaseManager import DatabaseManager
from ..util.DrawingUtils import DrawingUtils

class RestrictedAreaRepository:
    def __init__(self):
        self.storage_dir = DatabaseManager.STORAGE_PATHS["files"] / "restricted_violations"
        os.makedirs(self.storage_dir, exist_ok=True)
        self.db_manager = DatabaseManager()
        self.session: Session = self.db_manager.get_session("default")

    def save_area_violation(self, pipeline_id, worker_source_id, frame_id, tracked_objects, frame, frame_drawer):
        """
        Save restricted area violation event.
        """
        current_datetime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")  # Timestamp

        frame_drawer.draw_polygons(frame)

        for tracked_obj in tracked_objects:
            person_id = tracked_obj["uuid"]
            attributes = tracked_obj["attributes"]

            if not any((attr.get("label") == "in_restricted_area" and attr.get("count", 0) == 5) for attr in attributes):
                continue

            drawn_frame = frame_drawer.draw_frame(frame.copy(), [tracked_obj.copy()])

            # Save full frame image
            full_image_filename = f"{pipeline_id}_{person_id}_{current_datetime}.jpg"
            full_image_path = os.path.join(self.storage_dir, full_image_filename)
            cv2.imwrite(full_image_path, drawn_frame)

            # Save cropped image with buffer
            bbox = tracked_obj["bbox"]
            cropped_image, obj = DrawingUtils.crop_with_bounding_box(frame, tracked_obj)
            cropped_image = frame_drawer.draw_frame(cropped_image, [obj])

            cropped_image_filename = f"{pipeline_id}_{person_id}_{current_datetime}_cropped.jpg"
            cropped_image_path = os.path.join(self.storage_dir, cropped_image_filename)
            cv2.imwrite(cropped_image_path, cropped_image)

            try:
                new_detection = RestrictedAreaViolationEntity(
                    worker_source_id=worker_source_id,
                    person_id=person_id,
                    image_path=full_image_path,
                    image_tile_path=cropped_image_path,
                    confidence_score=tracked_obj.get("confidence", 1),
                    b_box_x1=bbox[0],
                    b_box_y1=bbox[1],
                    b_box_x2=bbox[2],
                    b_box_y2=bbox[3],
                )
                self.session.add(new_detection)
                self.session.flush()
                self.session.commit()
                logging.info(f"✅ Inserted restricted area violation for Person {person_id}")

                # Trigger detection callback
                try:
                    from ..core_service import CoreService
                    from ..detection.detection_processing.HumanDetectionProcessor import HumanDetectionProcessor
                    
                    # Create unified detection data using the processor's factory method
                    unified_data = HumanDetectionProcessor.create_detection_data(
                        pipeline_id=pipeline_id,
                        worker_source_id=worker_source_id,
                        person_id=person_id,
                        detection_id=new_detection.id if hasattr(new_detection, 'id') else f"area_{person_id}_{current_datetime}",
                        tracked_obj=tracked_obj,
                        image_path=full_image_path,
                        image_tile_path=cropped_image_path,
                        frame_id=frame_id
                    )
                    
                    # Trigger callbacks
                    CoreService.trigger_detection(unified_data)
                    
                except Exception as e:
                    logging.warning(f"⚠️ Failed to trigger area violation callback: {e}")

            except SQLAlchemyError as e:
                self.session.rollback()
                logging.error(f"❌ Database error while saving detection: {e}")
