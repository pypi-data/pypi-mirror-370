import logging
import threading
import time
import cv2
import queue
import uuid
from typing import Dict, Optional, Callable, List
from pathlib import Path
import tempfile
import json
import os


class SharedVideoStreamServer:
    """
    A shared video stream server that captures from a video device once
    and distributes frames to multiple consumers (both services).
    """
    
    _instances: Dict[int, 'SharedVideoStreamServer'] = {}
    _lock = threading.Lock()
    
    def __new__(cls, device_index: int):
        with cls._lock:
            if device_index not in cls._instances:
                cls._instances[device_index] = super().__new__(cls)
                cls._instances[device_index]._initialized = False
            return cls._instances[device_index]
    
    def __init__(self, device_index: int):
        if self._initialized:
            return
            
        self._initialized = True
        self.device_index = device_index
        self.cap = None
        self.running = False
        self.capture_thread = None
        self.frame_lock = threading.Lock()
        self.latest_frame = None
        self.frame_timestamp = 0
        
        # Consumer management
        self.consumers: Dict[str, Dict] = {}  # consumer_id -> {callback, last_frame_time}
        self.consumers_lock = threading.Lock()
        
        # Device properties
        self.width = 640
        self.height = 480
        self.fps = 30.0
        
        # Shared state file for cross-service coordination
        self.state_file = self._get_state_file_path()
        
        logging.info(f"SharedVideoStreamServer initialized for device {device_index}")
    
    def _get_state_file_path(self) -> Path:
        """Get the path for the shared state file."""
        temp_dir = tempfile.gettempdir()
        state_dir = Path(temp_dir) / "nedo-vision-shared-streams"
        state_dir.mkdir(exist_ok=True)
        return state_dir / f"device_{self.device_index}_state.json"
    
    def _update_state_file(self):
        """Update the shared state file with current server status."""
        try:
            state = {
                "device_index": self.device_index,
                "running": self.running,
                "pid": os.getpid(),
                "consumer_count": len(self.consumers),
                "width": self.width,
                "height": self.height,
                "fps": self.fps,
                "last_update": time.time()
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logging.warning(f"Failed to update state file: {e}")
    
    def _read_state_file(self) -> Optional[Dict]:
        """Read the shared state file."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
    
    def start_capture(self) -> bool:
        """Start capturing from the video device."""
        if self.running:
            logging.info(f"Device {self.device_index} capture already running")
            return True
        
        try:
            # Try to open the device
            self.cap = cv2.VideoCapture(self.device_index)
            
            if not self.cap.isOpened():
                logging.error(f"Cannot open video device {self.device_index}")
                return False
            
            # Get device properties
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = float(self.cap.get(cv2.CAP_PROP_FPS))
            
            if self.fps <= 0 or self.fps > 240:
                self.fps = 30.0
            
            logging.info(f"Device {self.device_index} opened: {self.width}x{self.height} @ {self.fps}fps")
            
            # Start capture thread
            self.running = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            
            # Update state file
            self._update_state_file()
            
            return True
            
        except Exception as e:
            logging.error(f"Error starting capture for device {self.device_index}: {e}")
            return False
    
    def stop_capture(self):
        """Stop capturing from the video device."""
        if not self.running:
            return
        
        logging.info(f"Stopping capture for device {self.device_index}")
        
        self.running = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=5)
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        # Clean up state file
        try:
            if self.state_file.exists():
                self.state_file.unlink()
        except Exception:
            pass
        
        # Remove from instances
        with self._lock:
            if self.device_index in self._instances:
                del self._instances[self.device_index]
    
    def _capture_loop(self):
        """Main capture loop that reads frames and distributes to consumers."""
        frame_interval = 1.0 / self.fps
        last_frame_time = 0
        
        while self.running and self.cap and self.cap.isOpened():
            try:
                current_time = time.time()
                
                # Throttle frame rate
                if current_time - last_frame_time < frame_interval:
                    time.sleep(0.001)
                    continue
                
                ret, frame = self.cap.read()
                
                if not ret or frame is None:
                    logging.warning(f"Failed to read frame from device {self.device_index}")
                    time.sleep(0.1)
                    continue
                
                # Update latest frame
                with self.frame_lock:
                    self.latest_frame = frame.copy()
                    self.frame_timestamp = current_time
                
                # Distribute frame to consumers
                self._distribute_frame(frame, current_time)
                
                last_frame_time = current_time
                
                # Update state file periodically
                if int(current_time) % 5 == 0:  # Every 5 seconds
                    self._update_state_file()
                
            except Exception as e:
                logging.error(f"Error in capture loop for device {self.device_index}: {e}")
                time.sleep(0.1)
        
        logging.info(f"Capture loop ended for device {self.device_index}")
    
    def _distribute_frame(self, frame, timestamp):
        """Distribute frame to all registered consumers."""
        with self.consumers_lock:
            dead_consumers = []
            
            for consumer_id, consumer_info in self.consumers.items():
                try:
                    callback = consumer_info['callback']
                    callback(frame, timestamp)
                    consumer_info['last_frame_time'] = timestamp
                    
                except Exception as e:
                    logging.warning(f"Error delivering frame to consumer {consumer_id}: {e}")
                    dead_consumers.append(consumer_id)
            
            # Remove dead consumers
            for consumer_id in dead_consumers:
                del self.consumers[consumer_id]
                logging.info(f"Removed dead consumer: {consumer_id}")
    
    def add_consumer(self, callback: Callable, consumer_id: str = None) -> str:
        """Add a consumer that will receive frames."""
        if consumer_id is None:
            consumer_id = str(uuid.uuid4())
        
        with self.consumers_lock:
            self.consumers[consumer_id] = {
                'callback': callback,
                'added_time': time.time(),
                'last_frame_time': 0
            }
        
        logging.info(f"Added consumer {consumer_id} for device {self.device_index}")
        
        # Start capture if this is the first consumer
        if len(self.consumers) == 1 and not self.running:
            self.start_capture()
        
        return consumer_id
    
    def remove_consumer(self, consumer_id: str):
        """Remove a consumer."""
        with self.consumers_lock:
            if consumer_id in self.consumers:
                del self.consumers[consumer_id]
                logging.info(f"Removed consumer {consumer_id} for device {self.device_index}")
        
        # Stop capture if no more consumers
        if len(self.consumers) == 0 and self.running:
            self.stop_capture()
    
    def get_latest_frame(self):
        """Get the latest captured frame."""
        with self.frame_lock:
            if self.latest_frame is not None:
                return self.latest_frame.copy(), self.frame_timestamp
        return None, 0
    
    def get_device_properties(self) -> tuple:
        """Get device properties."""
        return self.width, self.height, self.fps, "rgb24"
    
    def is_running(self) -> bool:
        """Check if the server is running."""
        return self.running
    
    def get_consumer_count(self) -> int:
        """Get the number of active consumers."""
        with self.consumers_lock:
            return len(self.consumers)


# Global function to get or create shared stream server
def get_shared_stream_server(device_index: int) -> SharedVideoStreamServer:
    """Get or create a shared stream server for a device."""
    return SharedVideoStreamServer(device_index)
