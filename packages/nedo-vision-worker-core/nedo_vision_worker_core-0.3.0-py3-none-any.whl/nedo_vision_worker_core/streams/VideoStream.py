import os
import cv2
import threading
import time
import logging
from typing import Optional, Union
from enum import Enum


class StreamState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    STOPPED = "stopped"


class VideoStream(threading.Thread):
    """Thread-safe video capture with automatic reconnection and error handling."""
    
    def __init__(
        self, 
        source: Union[str, int], 
        reconnect_interval: float = 5.0,
        max_failures: int = 5,
        max_reconnect_attempts: int = 10,
        backoff_factor: float = 1.5,
        target_fps: Optional[float] = None
    ):
        super().__init__(daemon=True)
        
        self.source = source
        self.reconnect_interval = reconnect_interval
        self.max_failures = max_failures
        self.max_reconnect_attempts = max_reconnect_attempts
        self.backoff_factor = backoff_factor
        self.target_fps = target_fps
        
        self.capture = None
        self.state = StreamState.DISCONNECTED
        self.fps = 30.0
        self.frame_count = 0
        self.start_time = time.time()
        
        self._running = True
        self._lock = threading.Lock()
        self._latest_frame = None
        self._reconnect_attempts = 0
        self._current_interval = reconnect_interval
        
        self.is_file = self._is_file_source()
        
    def _is_file_source(self) -> bool:
        """Check if source is a file path."""
        if isinstance(self.source, int):
            return False
        return isinstance(self.source, (str, bytes, os.PathLike)) and os.path.isfile(str(self.source))
    
    def _get_source_for_cv2(self) -> Union[str, int]:
        """Convert source to format suitable for cv2.VideoCapture."""
        if isinstance(self.source, str) and self.source.isdigit():
            return int(self.source)
        return self.source
    
    def _initialize_capture(self) -> bool:
        """Initialize video capture device."""
        try:
            self.state = StreamState.CONNECTING
            logging.info(f"Connecting to {self.source} (attempt {self._reconnect_attempts + 1})")
            
            if self.capture:
                self.capture.release()
            
            self.capture = cv2.VideoCapture(self._get_source_for_cv2())
            
            if not self.capture.isOpened():
                logging.error(f"Failed to open video source: {self.source}")
                return False
            
            self._configure_capture()
            self.state = StreamState.CONNECTED
            return True
            
        except Exception as e:
            logging.error(f"Error initializing capture: {e}")
            self._cleanup_capture()
            return False
    
    def _configure_capture(self):
        """Configure capture properties and determine FPS."""
        detected_fps = self.capture.get(cv2.CAP_PROP_FPS)
        
        if self.target_fps:
            self.fps = self.target_fps
            if hasattr(cv2, 'CAP_PROP_FPS'):
                self.capture.set(cv2.CAP_PROP_FPS, self.target_fps)
        elif detected_fps and 0 < detected_fps <= 240:
            self.fps = detected_fps
        else:
            self.fps = 30.0
            logging.warning(f"Invalid FPS detected ({detected_fps}), using {self.fps}")
        
        if self.is_file:
            total_frames = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = total_frames / self.fps if self.fps > 0 else 0
            logging.info(f"Video file: {self.fps:.1f} FPS, {int(total_frames)} frames, {duration:.1f}s")
        else:
            logging.info(f"Stream connected: {self.fps:.1f} FPS")
    
    def _cleanup_capture(self):
        """Clean up capture resources."""
        if self.capture:
            try:
                self.capture.release()
            except Exception as e:
                logging.error(f"Error releasing capture: {e}")
            finally:
                self.capture = None
        self.state = StreamState.DISCONNECTED
    
    def _handle_reconnection(self) -> bool:
        """Handle reconnection logic with backoff."""
        if self._reconnect_attempts >= self.max_reconnect_attempts:
            logging.error(f"Max reconnection attempts reached for {self.source}")
            return False
        
        self._reconnect_attempts += 1
        self.state = StreamState.RECONNECTING
        self._current_interval = min(self._current_interval * self.backoff_factor, 60.0)
        
        logging.warning(f"Reconnecting in {self._current_interval:.1f}s...")
        return self._sleep_interruptible(self._current_interval)
    
    def _sleep_interruptible(self, duration: float) -> bool:
        """Sleep with ability to interrupt on stop."""
        end_time = time.time() + duration
        while time.time() < end_time and self._running:
            time.sleep(0.1)
        return self._running
    
    def _handle_file_end(self) -> bool:
        """Handle video file reaching end."""
        if not self.is_file:
            return False
        
        try:
            current_pos = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
            total_frames = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
            
            if current_pos >= total_frames - 1:
                logging.info(f"Video file ended, restarting: {self.source}")
                self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                return True
        except Exception as e:
            logging.error(f"Error handling file end: {e}")
        
        return False
    
    def run(self):
        """Main capture loop."""
        failure_count = 0
        frame_interval = 1.0 / self.fps
        
        while self._running:
            try:
                if not self.capture or not self.capture.isOpened():
                    if not self._initialize_capture():
                        if not self._handle_reconnection():
                            break
                        continue
                    
                    failure_count = 0
                    self._reconnect_attempts = 0
                    self._current_interval = self.reconnect_interval
                    frame_interval = 1.0 / self.fps
                
                start_time = time.time()
                ret, frame = self.capture.read()
                
                if not ret or frame is None or frame.size == 0:
                    if self._handle_file_end():
                        continue
                    
                    failure_count += 1
                    if failure_count > self.max_failures:
                        logging.error("Too many consecutive failures, reconnecting...")
                        self._cleanup_capture()
                        failure_count = 0
                        continue
                    
                    if not self._sleep_interruptible(0.1):
                        break
                    continue
                
                failure_count = 0
                self.frame_count += 1
                
                with self._lock:
                    if self._running:
                        self._latest_frame = frame.copy()
                
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0 and not self._sleep_interruptible(sleep_time):
                    break
                    
            except cv2.error as e:
                logging.error(f"OpenCV error: {e}")
                self._cleanup_capture()
                if not self._sleep_interruptible(1.0):
                    break
                    
            except Exception as e:
                logging.error(f"Unexpected error: {e}", exc_info=True)
                if not self._sleep_interruptible(self.reconnect_interval):
                    break
        
        self._final_cleanup()
    
    def _final_cleanup(self):
        """Final resource cleanup."""
        self.state = StreamState.STOPPED
        self._cleanup_capture()
        
        with self._lock:
            self._latest_frame = None
        
        logging.info(f"VideoStream stopped: {self.source}")
    
    def get_frame(self) -> Optional[cv2.Mat]:
        """Get the latest frame (thread-safe)."""
        if not self._running or self.state not in (StreamState.CONNECTED, StreamState.RECONNECTING):
            return None
        
        with self._lock:
            return self._latest_frame.copy() if self._latest_frame is not None else None
    
    def is_connected(self) -> bool:
        """Check if stream is currently connected."""
        return self.state == StreamState.CONNECTED
    
    @property
    def running(self) -> bool:
        """Check if stream is currently running."""
        return self._running and self.state != StreamState.STOPPED
    
    def get_state(self) -> StreamState:
        """Get current stream state."""
        return self.state
    
    def is_video_ended(self) -> bool:
        """Check if video file has ended."""
        if not self.is_file or not self.capture:
            return False
        
        try:
            current_pos = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
            total_frames = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
            return current_pos >= total_frames - 1
        except Exception:
            return False
    
    def stop(self, timeout: float = 5.0):
        """Stop the video stream gracefully."""
        if not self._running:
            return
        
        logging.info(f"Stopping VideoStream: {self.source}")
        self._running = False
        
        with self._lock:
            self._latest_frame = None
        
        if self.is_alive():
            self.join(timeout=timeout)
            if self.is_alive():
                logging.warning(f"Stream thread did not exit within {timeout}s")
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()