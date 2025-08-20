"""
Nedo Vision Core Library

A library for running AI vision processing and detection in the Nedo Vision platform.
"""

from .core_service import CoreService
from .callbacks import DetectionType, CallbackTrigger, DetectionData, IntervalMetadata

__version__ = "0.3.0"
__all__ = [
    "CoreService", 
    "DetectionType", 
    "CallbackTrigger", 
    "DetectionData",
    "IntervalMetadata",
    "DetectionAttribute",
    "BoundingBox"
]

# Convenience functions for common callback patterns
def register_immediate_ppe_callback(name: str, callback):
    """Register an immediate PPE detection callback."""
    return CoreService.register_callback(
        name=name,
        callback=callback,
        trigger=CallbackTrigger.ON_NEW_DETECTION,
        detection_types=[DetectionType.PPE_DETECTION]
    )

def register_immediate_area_callback(name: str, callback):
    """Register an immediate area violation callback."""
    return CoreService.register_callback(
        name=name,
        callback=callback,
        trigger=CallbackTrigger.ON_NEW_DETECTION,
        detection_types=[DetectionType.AREA_VIOLATION]
    )

def register_interval_ppe_callback(name: str, callback, interval_seconds: int = 60):
    """Register an interval-based PPE violation summary callback."""
    return CoreService.register_callback(
        name=name,
        callback=callback,
        trigger=CallbackTrigger.ON_VIOLATION_INTERVAL,
        detection_types=[DetectionType.PPE_DETECTION],
        interval_seconds=interval_seconds
    )

def register_interval_area_callback(name: str, callback, interval_seconds: int = 60):
    """Register an interval-based area violation summary callback."""
    return CoreService.register_callback(
        name=name,
        callback=callback,
        trigger=CallbackTrigger.ON_VIOLATION_INTERVAL,
        detection_types=[DetectionType.AREA_VIOLATION],
        interval_seconds=interval_seconds
    )