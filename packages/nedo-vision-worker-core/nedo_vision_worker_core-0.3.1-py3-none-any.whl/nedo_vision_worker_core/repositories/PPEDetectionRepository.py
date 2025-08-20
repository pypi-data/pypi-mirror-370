import os
import cv2
import datetime
import uuid
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..database.DatabaseManager import DatabaseManager
from ..models.ppe_detection import PPEDetectionEntity
from ..models.ppe_detection_label import PPEDetectionLabelEntity
from ..util.DrawingUtils import DrawingUtils

class PPEDetectionRepository:
    """Handles storage of PPE detections into SQLite using SQLAlchemy."""

    def __init__(self):
        
        self.storage_dir = DatabaseManager.STORAGE_PATHS["files"] / "ppe_detections"
        self.db_manager = DatabaseManager()
        self.session: Session = self.db_manager.get_session("default")
        os.makedirs(self.storage_dir, exist_ok=True) 

    def save_ppe_detection(self, pipeline_id, worker_source_id, frame_id, tracked_objects, frame, frame_drawer):
        """
        Inserts new detections only if at least one attribute's detection count is >= 5.

        Args:
            pipeline_id (str): Unique ID of the video pipeline.
            worker_source_id (str): Source of the video stream.
            frame_id (int): Frame number.
            tracked_objects (list): List of detected persons and their attribute counts.
            frame (numpy.ndarray): Image frame for saving snapshots.
        """
        current_datetime = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")  # Timestamp

        for tracked_obj in tracked_objects:
            person_id = tracked_obj["uuid"]
            attributes = tracked_obj["attributes"]
            valid_attributes = []

            if not any(attr.get("count", 0) == 5 for attr in attributes):
                continue  # Skip this detection

            filtered_attributes = [attr for attr in attributes if attr.get("count", 0) >= 5]
            
            draw_obj = tracked_obj.copy()
            draw_obj["attributes"] = filtered_attributes
            
            drawn_frame = frame_drawer.draw_frame(frame.copy(), [draw_obj])

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
                new_detection = PPEDetectionEntity(
                    id=str(uuid.uuid4()),
                    worker_id=pipeline_id,
                    worker_source_id=worker_source_id,
                    person_id=person_id,
                    image_path=full_image_path,
                    image_tile_path=cropped_image_path,
                    b_box_x1=bbox[0],
                    b_box_y1=bbox[1],
                    b_box_x2=bbox[2],
                    b_box_y2=bbox[3],
                    detection_count=tracked_obj.get("detections", 0)
                )
                self.session.add(new_detection)
                self.session.flush()

                for attr in filtered_attributes:
                    label = attr["label"]
                    valid_attributes.append(label)

                    if attr and "bbox" in attr:
                        attr_bbox = attr["bbox"]
                        # Assuming attr_bbox is in [x, y, width, height] format.
                        attr_b_box_x1 = attr_bbox[0]
                        attr_b_box_y1 = attr_bbox[1]
                        attr_b_box_x2 = attr_bbox[2]
                        attr_b_box_y2 = attr_bbox[3]
                    else:
                        # Fallback to default values if the attribute bbox is not available.
                        attr_b_box_x1 = 0.0
                        attr_b_box_y1 = 0.0
                        attr_b_box_x2 = 0.0
                        attr_b_box_y2 = 0.0

                    # Retrieve confidence score; default to 1.0 if not available.
                    if attr:
                        confidence_score = attr.get("confidence", 1.0)
                    else:
                        confidence_score = 1.0

                    new_label = PPEDetectionLabelEntity(
                        id=str(uuid.uuid4()),
                        detection_id=new_detection.id,
                        code=label,
                        confidence_score=confidence_score,
                        detection_count=attr.get("count", 0),
                        b_box_x1=attr_b_box_x1,
                        b_box_y1=attr_b_box_y1,
                        b_box_x2=attr_b_box_x2,
                        b_box_y2=attr_b_box_y2
                    )
                    self.session.add(new_label)

                self.session.commit()
                logging.info(f"✅ Inserted detection for Person {person_id}, Attributes: {valid_attributes}")

                # Trigger detection callback with unified data structure
                try:
                    from ..core_service import CoreService
                    from ..detection.detection_processing.PPEDetectionProcessor import PPEDetectionProcessor
                    
                    # Create unified detection data using the processor's factory method
                    unified_data = PPEDetectionProcessor.create_detection_data(
                        pipeline_id=pipeline_id,
                        worker_source_id=worker_source_id,
                        person_id=person_id,
                        detection_id=new_detection.id,
                        tracked_obj=tracked_obj,
                        image_path=full_image_path,
                        image_tile_path=cropped_image_path,
                        frame_id=frame_id
                    )
                    
                    # Trigger callbacks
                    CoreService.trigger_detection(unified_data)
                    
                except Exception as e:
                    logging.warning(f"⚠️ Failed to trigger PPE detection callback: {e}")

            except SQLAlchemyError as e:
                self.session.rollback()
                logging.error(f"❌ Database error while saving detection: {e}")

