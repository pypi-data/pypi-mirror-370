from typing import List
from shapely.geometry import Polygon, Point

class PersonRestrictedAreaMatcher:
    """Matches detected persons with restricted areas defined as polygons."""
    
    @staticmethod
    def match_persons_with_restricted_areas(persons, restricted_areas: List[Polygon]):
        """
        Correlates detected persons with restricted areas defined as polygons.
        Using center point method for detection.
        
        Args:
            persons (list): List of person detections (each detection has 'bbox').
            restricted_areas (list): List of restricted areas, each defined as a polygon with coordinates.
            
        Returns:
            list: List of persons with matched restricted areas they've entered.
        """
        matched_results = []
        
        for person in persons:
            person_bbox = person["bbox"]
            
            # Calculate center point of person's bounding box
            # bbox format is typically [x_min, y_min, x_max, y_max]
            center_x = (person_bbox[0] + person_bbox[2]) / 2
            center_y = (person_bbox[1] + person_bbox[3]) / 2
            center_point = Point(center_x, center_y)
            
            in_restricted = any(area.contains(center_point) for area in restricted_areas)

            attributes = [{
                "label": "in_restricted_area",
                "confidence": 1.0,
            }] if in_restricted else []

            matched_results.append({
                "label": "person",
                "confidence": person["confidence"],
                "bbox": person_bbox,
                "attributes": attributes
            })
            
        return matched_results