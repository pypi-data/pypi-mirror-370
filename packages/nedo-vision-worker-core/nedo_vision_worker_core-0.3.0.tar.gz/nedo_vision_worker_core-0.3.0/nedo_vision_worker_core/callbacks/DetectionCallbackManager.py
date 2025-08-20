"""
Callback management system for detection events.
Supports immediate callbacks (triggered on each detection) and interval-based callbacks
(triggered periodically based on current violation state).
"""

import logging
import threading
import time
from typing import Callable, Dict, List, Any, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass

from .DetectionCallbackTypes import DetectionType, CallbackTrigger, DetectionData


@dataclass
class CallbackConfig:
    """Configuration for a registered callback."""
    callback: Callable[[DetectionData], None]
    trigger: CallbackTrigger
    detection_types: List[DetectionType]
    interval_seconds: Optional[int] = None
    
    def __post_init__(self):
        if self.trigger == CallbackTrigger.ON_VIOLATION_INTERVAL and self.interval_seconds is None:
            raise ValueError("interval_seconds is required for ON_VIOLATION_INTERVAL callbacks")


class DetectionCallbackManager:
    """Callback manager with support for immediate and current-state interval callbacks."""
    
    def __init__(self):
        self._callbacks: Dict[str, CallbackConfig] = {}
        self._current_violations: Dict[str, DetectionData] = {}  # Current active violations by key
        self._interval_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()
        self._last_interval_trigger: Dict[int, datetime] = {}  # Track last trigger time per interval
        
        self._start_interval_thread()
    
    def register_callback(self, 
                         name: str,
                         callback: Callable[[DetectionData], None],
                         trigger: CallbackTrigger,
                         detection_types: List[DetectionType],
                         interval_seconds: Optional[int] = None) -> None:
        """
        Register a detection callback.
        
        Args:
            name: Unique name for the callback
            callback: Function to call when detection occurs
            trigger: When to trigger the callback (immediate or interval)
            detection_types: Types of detections to listen for
            interval_seconds: For interval callbacks, how often to call (in seconds)
        """
        with self._lock:
            config = CallbackConfig(
                callback=callback,
                trigger=trigger,
                detection_types=detection_types,
                interval_seconds=interval_seconds
            )
            
            self._callbacks[name] = config
            logging.info(f"📞 Registered callback '{name}' for {[dt.value for dt in detection_types]} "
                        f"with trigger {trigger.value}")
    
    def unregister_callback(self, name: str) -> bool:
        """
        Unregister a callback.
        
        Args:
            name: Name of the callback to remove
            
        Returns:
            True if callback was found and removed, False otherwise
        """
        with self._lock:
            if name in self._callbacks:
                del self._callbacks[name]
                logging.info(f"📞 Unregistered callback '{name}'")
                return True
            return False
    
    def trigger_detection(self, detection_data: DetectionData) -> None:
        """
        Trigger callbacks for a new detection.
        Callbacks consume the data as-is, with no modification of detection logic.
        
        Args:
            detection_data: The detection data to process
        """
        with self._lock:
            key = f"{detection_data.pipeline_id}_{detection_data.person_id}_{detection_data.detection_type.value}"
            
            # Store current violations (only if they have violations)
            if detection_data.has_violations():
                self._current_violations[key] = detection_data
            else:
                # Remove from current violations if no longer violating
                self._current_violations.pop(key, None)
            
            # Trigger immediate callbacks for all detections (including non-violations)
            self._trigger_immediate_callbacks(detection_data)
    
    def _trigger_immediate_callbacks(self, detection_data: DetectionData) -> None:
        """Trigger callbacks that should fire immediately on new detections."""
        for name, config in self._callbacks.items():
            if (config.trigger == CallbackTrigger.ON_NEW_DETECTION and 
                detection_data.detection_type in config.detection_types):
                
                try:
                    config.callback(detection_data)
                except Exception as e:
                    logging.error(f"❌ Error in callback '{name}': {e}")
    
    def _start_interval_thread(self) -> None:
        """Start the background thread for interval-based callbacks."""
        self._interval_thread = threading.Thread(
            target=self._interval_processor,
            name="DetectionCallbackInterval",
            daemon=True
        )
        self._interval_thread.start()
        logging.info("🔄 Started detection callback interval processor")
    
    def _interval_processor(self) -> None:
        """Background thread that processes interval-based callbacks."""
        while not self._stop_event.is_set():
            try:
                interval_groups = defaultdict(list)
                with self._lock:
                    for name, config in self._callbacks.items():
                        if config.trigger == CallbackTrigger.ON_VIOLATION_INTERVAL:
                            interval_groups[config.interval_seconds].append((name, config))
                
                current_time = datetime.utcnow()
                
                # Clean up stale violations
                self._cleanup_stale_violations(current_time)
                
                for interval_seconds, callbacks in interval_groups.items():
                    self._process_interval_group(current_time, interval_seconds, callbacks)
                
                self._stop_event.wait(1.0)
                
            except Exception as e:
                logging.error(f"❌ Error in interval processor: {e}")
                time.sleep(1.0)
    
    def _process_interval_group(self, current_time: datetime, interval_seconds: int, 
                               callbacks: List[tuple]) -> None:
        """Process callbacks for a specific interval. Only triggers when violations are currently active."""
        # Check if enough time has passed for this interval
        last_trigger = self._last_interval_trigger.get(interval_seconds)
        if last_trigger and (current_time - last_trigger).total_seconds() < interval_seconds:
            return  # Not time yet for this interval
        
        with self._lock:
            if not self._current_violations:
                return
            
            # Only process violations that are still current (updated recently)
            recent_threshold = timedelta(seconds=3)  # Must be updated within last 3 seconds
            current_violations = []
            for violation in self._current_violations.values():
                if current_time - violation.timestamp <= recent_threshold:
                    current_violations.append(violation)
            
            if not current_violations:
                return
            
            current_violation_summary = self._create_current_state_summary(
                current_violations, current_time
            )
            
            if not current_violation_summary:
                return
            
            # Update last trigger time for this interval
            self._last_interval_trigger[interval_seconds] = current_time
            
            for summary in current_violation_summary:
                for name, config in callbacks:
                    if summary.detection_type in config.detection_types:
                        try:
                            config.callback(summary)
                        except Exception as e:
                            logging.error(f"❌ Error in interval callback '{name}': {e}")
    
    def _create_current_state_summary(self, current_violations: List[DetectionData], current_time: datetime) -> List[DetectionData]:
        """Create current state detection data from active violations."""
        if not current_violations:
            return []
        
        # Group by detection type and pipeline
        groups = defaultdict(list)
        for violation in current_violations:
            key = f"{violation.detection_type.value}_{violation.pipeline_id}"
            groups[key].append(violation)
        
        summaries = []
        for group_violations in groups.values():
            if not group_violations:
                continue
                
            latest = max(group_violations, key=lambda v: v.timestamp)
            
            current_violation_counts = defaultdict(int)
            total_current_violations = 0
            
            for violation in group_violations:
                for attr in violation.get_violations():
                    current_violation_counts[attr.label] += 1
                    total_current_violations += 1
            
            if total_current_violations == 0:
                continue
            
            metadata = {
                'current_violation_state': dict(current_violation_counts),
                'total_active_violations': total_current_violations,
                'unique_persons_in_violation': len(set(v.person_id for v in group_violations)),
                'state_timestamp': current_time.isoformat()
            }
            
            summary = DetectionData(
                detection_type=latest.detection_type,
                detection_id=f"current_state_{latest.detection_type.value}_{int(time.time())}",
                person_id="multiple" if len(set(v.person_id for v in group_violations)) > 1 else latest.person_id,
                pipeline_id=latest.pipeline_id,
                worker_source_id=latest.worker_source_id,
                confidence_score=sum(v.confidence_score for v in group_violations) / len(group_violations),
                bbox=latest.bbox,
                attributes=latest.get_violations(),
                image_path=latest.image_path,
                image_tile_path=latest.image_tile_path,
                timestamp=current_time,
                frame_id=latest.frame_id,
                metadata=metadata
            )
            
            summaries.append(summary)
        
        return summaries

    def _cleanup_stale_violations(self, current_time: datetime) -> None:
        """Remove violations that haven't been updated recently (stale detections)."""
        stale_threshold = timedelta(seconds=5)  # More aggressive cleanup
        stale_keys = []
        
        for key, violation_data in self._current_violations.items():
            if current_time - violation_data.timestamp > stale_threshold:
                stale_keys.append(key)
                logging.debug(f"🧹 Removing stale violation: {key} (age: {current_time - violation_data.timestamp})")
        
        for key in stale_keys:
            self._current_violations.pop(key, None)
    
    def get_callback_stats(self) -> Dict[str, Any]:
        """Get statistics about registered callbacks and recent activity."""
        with self._lock:
            immediate_callbacks = sum(1 for c in self._callbacks.values() 
                                    if c.trigger == CallbackTrigger.ON_NEW_DETECTION)
            interval_callbacks = sum(1 for c in self._callbacks.values() 
                                   if c.trigger == CallbackTrigger.ON_VIOLATION_INTERVAL)
            
            return {
                'total_callbacks': len(self._callbacks),
                'immediate_callbacks': immediate_callbacks,
                'interval_callbacks': interval_callbacks,
                'current_active_violations': len(self._current_violations),
                'callback_names': list(self._callbacks.keys())
            }
    
    def list_callbacks(self) -> Dict[str, Dict[str, Any]]:
        """List all registered callbacks with their configurations."""
        with self._lock:
            result = {}
            for name, config in self._callbacks.items():
                result[name] = {
                    'trigger': config.trigger.value,
                    'detection_types': [dt.value for dt in config.detection_types],
                    'interval_seconds': config.interval_seconds,
                    'callback_name': config.callback.__name__
                }
            return result
    
    def stop(self) -> None:
        """Stop the callback manager and cleanup resources."""
        logging.info("🛑 Stopping detection callback manager...")
        self._stop_event.set()
        
        if self._interval_thread and self._interval_thread.is_alive():
            self._interval_thread.join(timeout=5.0)
        
        with self._lock:
            self._callbacks.clear()
            self._current_violations.clear()
            self._last_interval_trigger.clear()
        
        logging.info("✅ Detection callback manager stopped")