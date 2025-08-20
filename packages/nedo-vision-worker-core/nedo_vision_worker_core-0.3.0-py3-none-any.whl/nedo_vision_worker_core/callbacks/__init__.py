"""
Detection callback system for Nedo Vision Worker Core.
"""

from .DetectionCallbackTypes import (
    CallbackTrigger,
    DetectionType, 
    DetectionAttribute,
    BoundingBox,
    DetectionData,
    IntervalMetadata
)

from .DetectionCallbackManager import (
    DetectionCallbackManager,
    CallbackConfig
)

__all__ = [
    'DetectionCallbackManager',
    'CallbackTrigger',
    'DetectionType',
    'DetectionAttribute', 
    'BoundingBox',
    'DetectionData',
    'IntervalMetadata'
]
