"""
Detection callback types and unified data structures.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict
from datetime import datetime
from enum import Enum


class DetectionType(Enum):
    """Types of detections."""
    PPE_DETECTION = "ppe_detection"
    AREA_VIOLATION = "area_violation"
    GENERAL_DETECTION = "general_detection"


class CallbackTrigger(Enum):
    """When callbacks should be triggered."""
    ON_NEW_DETECTION = "on_new_detection"
    ON_VIOLATION_INTERVAL = "on_violation_interval"


class IntervalMetadata(TypedDict):
    """Metadata structure for interval-based callbacks with current state."""
    current_violation_state: Dict[str, int]  # violation_type -> current count
    total_active_violations: int
    unique_persons_in_violation: int
    state_timestamp: str  # ISO format datetime when state was captured


@dataclass
class BoundingBox:
    """Unified bounding box representation."""
    x1: float
    y1: float
    x2: float
    y2: float
    
    @classmethod
    def from_list(cls, bbox: List[float]) -> 'BoundingBox':
        """Create BoundingBox from list [x1, y1, x2, y2]."""
        return cls(x1=bbox[0], y1=bbox[1], x2=bbox[2], y2=bbox[3])
    
    def to_list(self) -> List[float]:
        """Convert to list format [x1, y1, x2, y2]."""
        return [self.x1, self.y1, self.x2, self.y2]


@dataclass
class DetectionAttribute:
    """Represents a detection attribute (e.g., PPE violations)."""
    label: str
    confidence: float
    count: int = 0
    bbox: Optional[BoundingBox] = None
    is_violation: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            'label': self.label,
            'confidence': self.confidence,
            'count': self.count,
            'is_violation': self.is_violation
        }
        if self.bbox:
            result['bbox'] = self.bbox.to_list()
        return result


@dataclass
class DetectionData:
    """Unified data structure for all detection types."""
    
    # Core identification
    detection_type: DetectionType
    detection_id: str
    person_id: str
    pipeline_id: str
    worker_source_id: str
    
    # Detection details
    confidence_score: float
    bbox: BoundingBox
    attributes: List[DetectionAttribute] = field(default_factory=list)
    
    # Images
    image_path: str = ""
    image_tile_path: str = ""
    
    # Timing
    timestamp: datetime = field(default_factory=datetime.utcnow)
    frame_id: int = 0
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_violations(self) -> List[DetectionAttribute]:
        """Get only violation attributes."""
        return [attr for attr in self.attributes if attr.is_violation]
    
    def get_compliance(self) -> List[DetectionAttribute]:
        """Get only compliance attributes."""
        return [attr for attr in self.attributes if not attr.is_violation]
    
    def has_violations(self) -> bool:
        """Check if detection has any violations."""
        return len(self.get_violations()) > 0
    
    def get_interval_metadata(self) -> Optional[IntervalMetadata]:
        """Get typed metadata for interval callbacks."""
        if not self.metadata:
            return None
        
        # Check if this looks like interval metadata
        required_keys = {'current_violation_state', 'total_active_violations', 
                        'unique_persons_in_violation', 'state_timestamp'}
        if not required_keys.issubset(self.metadata.keys()):
            return None
        
        # Return typed metadata
        return IntervalMetadata(
            current_violation_state=self.metadata['current_violation_state'],
            total_active_violations=self.metadata['total_active_violations'],
            unique_persons_in_violation=self.metadata['unique_persons_in_violation'],
            state_timestamp=self.metadata['state_timestamp']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation for backward compatibility."""
        return {
            'type': self.detection_type.value,
            'detection_id': self.detection_id,
            'person_id': self.person_id,
            'pipeline_id': self.pipeline_id,
            'worker_source_id': self.worker_source_id,
            'confidence_score': self.confidence_score,
            'bbox': self.bbox.to_list(),
            'attributes': [attr.to_dict() for attr in self.attributes],
            'violations': [attr.to_dict() for attr in self.get_violations()],
            'compliance': [attr.to_dict() for attr in self.get_compliance()],
            'image_path': self.image_path,
            'image_tile_path': self.image_tile_path,
            'timestamp': self.timestamp.isoformat(),
            'frame_id': self.frame_id,
            'has_violations': self.has_violations(),
            'metadata': self.metadata
        }
