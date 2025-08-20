import logging
import threading
import time
import cv2
from typing import Dict, Optional, Callable
from enum import Enum
from .VideoStream import VideoStream
from ..services.SharedVideoStreamServer import get_shared_stream_server
from ..services.VideoSharingDaemonManager import get_daemon_manager

try:
    from nedo_vision_worker_core.services.VideoSharingDaemon import VideoSharingClient
except ImportError:
    logging.warning("Video sharing daemon not available, falling back to SharedVideoStreamServer")
    VideoSharingClient = None

try:
    from ..database.DatabaseManager import DatabaseManager
except ImportError:
    DatabaseManager = None


class DeviceAccessMode(Enum):
    EXCLUSIVE = "exclusive"
    SHARED = "shared"


class SharedVideoDeviceManager:
    """
    Manages shared access to direct video devices across multiple services.
    Prevents 'device busy' errors by implementing a device sharing mechanism.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.device_streams: Dict[int, VideoStream] = {}  # device_index -> VideoStream (legacy)
        self.device_subscribers: Dict[int, Dict[str, Callable]] = {}  # device_index -> {subscriber_id: callback}
        self.device_locks: Dict[int, threading.Lock] = {}
        self.device_access_counts: Dict[int, int] = {}
        self.main_lock = threading.Lock()
        
        # Video sharing clients for cross-process access
        self.video_clients = {}  # device_index -> Video sharing client
        self._use_video_sharing = VideoSharingClient is not None
        
        if self._use_video_sharing:
            logging.info("🔗 SharedVideoDeviceManager initialized with cross-process video sharing support")
        else:
            logging.info("⚠️ SharedVideoDeviceManager initialized with SharedVideoStreamServer fallback")
        
        logging.info("SharedVideoDeviceManager initialized")
    
    def _is_direct_device(self, source) -> tuple:
        """Check if source is a direct video device and return device index."""
        if isinstance(source, int):
            return True, source
        elif isinstance(source, str) and source.isdigit():
            return True, int(source)
        elif isinstance(source, str) and source.startswith('/dev/video'):
            try:
                device_index = int(source.replace('/dev/video', ''))
                return True, device_index
            except ValueError:
                pass
        return False, None
    
    def subscribe_to_device(self, source, subscriber_id: str, callback: Callable[[cv2.Mat], None]) -> bool:
        """
        Subscribe to a direct video device.
        
        Args:
            source: Video source (device index or path)
            subscriber_id: Unique identifier for the subscriber
            callback: Function to call with new frames
            
        Returns:
            bool: True if subscription successful, False otherwise
        """
        is_device, device_index = self._is_direct_device(source)
        
        if not is_device:
            logging.warning(f"Source {source} is not a direct video device")
            return False
        
        with self.main_lock:
            # Initialize device if not exists
            if device_index not in self.device_streams:
                if not self._initialize_device(device_index):
                    return False
            
            # Add subscriber
            if device_index not in self.device_subscribers:
                self.device_subscribers[device_index] = {}
            
            self.device_subscribers[device_index][subscriber_id] = callback
            self.device_access_counts[device_index] = self.device_access_counts.get(device_index, 0) + 1
            
            logging.info(f"Subscriber {subscriber_id} added to device {device_index}. "
                        f"Total subscribers: {self.device_access_counts[device_index]}")
            
            return True
    
    def unsubscribe_from_device(self, source, subscriber_id: str) -> bool:
        """
        Unsubscribe from a direct video device.
        
        Args:
            source: Video source (device index or path)
            subscriber_id: Unique identifier for the subscriber
            
        Returns:
            bool: True if unsubscription successful, False otherwise
        """
        is_device, device_index = self._is_direct_device(source)
        
        if not is_device:
            return False
        
        with self.main_lock:
            if device_index not in self.device_subscribers:
                return False
            
            if subscriber_id in self.device_subscribers[device_index]:
                del self.device_subscribers[device_index][subscriber_id]
                self.device_access_counts[device_index] -= 1
                
                logging.info(f"Subscriber {subscriber_id} removed from device {device_index}. "
                            f"Remaining subscribers: {self.device_access_counts[device_index]}")
                
                # Clean up device if no more subscribers
                if self.device_access_counts[device_index] <= 0:
                    self._cleanup_device(device_index)
                
                return True
        
        return False
    
    def _initialize_device(self, device_index: int) -> bool:
        """Initialize a direct video device with cross-process video sharing."""
        try:
            if self._use_video_sharing:
                return self._initialize_device_with_video_sharing(device_index)
            else:
                return self._initialize_device_with_shared_server(device_index)
        except Exception as e:
            logging.error(f"❌ Failed to initialize device {device_index}: {e}")
            return False

    def _initialize_device_with_video_sharing(self, device_index: int) -> bool:
        """Initialize device using VideoSharingClient for true cross-process access."""
        try:
            logging.info(f"Initializing cross-process access to video device {device_index}")
            
            # Ensure daemon is running for this device
            daemon_manager = get_daemon_manager()
            if not daemon_manager.ensure_daemon_for_device(device_index):
                logging.error(f"❌ Failed to ensure video sharing daemon for device {device_index}")
                return False
            
            # Get storage path from DatabaseManager
            storage_path = None
            if DatabaseManager and hasattr(DatabaseManager, 'STORAGE_PATH') and DatabaseManager.STORAGE_PATH:
                storage_path = str(DatabaseManager.STORAGE_PATH)
            
            # Create video sharing client
            video_client = VideoSharingClient(device_index, storage_path=storage_path)
            
            # Connect to the video sharing daemon
            if not video_client.connect(lambda frame, timestamp: self._on_frame_received(device_index, frame, timestamp)):
                logging.error(f"❌ Failed to connect to video sharing daemon for device {device_index}")
                logging.info("💡 Daemon should be auto-started, but connection failed")
                return False
            
            # Store video client
            self.video_clients[device_index] = video_client
            self.device_locks[device_index] = threading.Lock()
            
            # Store device info
            self.device_streams[device_index] = {
                'video_client': video_client,
                'type': 'video_sharing'
            }
            
            logging.info(f"✅ Successfully initialized cross-process access to device {device_index}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to initialize cross-process access for device {device_index}: {e}")
            return False

    def _initialize_device_with_shared_server(self, device_index: int) -> bool:
        """Initialize device using SharedVideoStreamServer (fallback method)."""
        try:
            logging.info(f"Initializing shared access to video device {device_index}")
            
            # Use shared stream server instead of exclusive device access
            shared_server = get_shared_stream_server(device_index)
            
            # Add this manager as a consumer
            consumer_id = shared_server.add_consumer(
                lambda frame, timestamp: self._on_frame_received(device_index, frame, timestamp),
                f"worker-core-{device_index}"
            )
            
            # Store server reference and consumer ID
            self.device_streams[device_index] = {
                'shared_server': shared_server,
                'consumer_id': consumer_id,
                'type': 'shared'
            }
            self.device_locks[device_index] = threading.Lock()
            
            logging.info(f"✅ Successfully initialized shared access to device {device_index}")
            return True
                
        except Exception as e:
            logging.error(f"❌ Failed to initialize shared access for device {device_index}: {e}")
            return False
    
    def _on_frame_received(self, device_index: int, frame, timestamp):
        """Handle frame received from shared stream server."""
        try:
            # Distribute frame to all subscribers
            with self.device_locks[device_index]:
                subscribers = self.device_subscribers.get(device_index, {}).copy()
            
            for subscriber_id, callback in subscribers.items():
                try:
                    callback(frame)
                except Exception as e:
                    logging.warning(f"Error delivering frame to subscriber {subscriber_id}: {e}")
                    
        except Exception as e:
            logging.error(f"Error processing frame for device {device_index}: {e}")
            
            logging.info(f"Successfully initialized shared access to device {device_index}")
            return True
            
        except Exception as e:
            logging.error(f"Error initializing device {device_index}: {e}")
            return False
    
    def _cleanup_device(self, device_index: int):
        """Clean up resources for a device and release shared stream access."""
        logging.info(f"Cleaning up device {device_index}")
        
        if device_index in self.device_streams:
            device_info = self.device_streams.pop(device_index)
            
            if isinstance(device_info, dict):
                device_type = device_info.get('type')
                
                if device_type == 'video_sharing':
                    # Disconnect from video sharing client
                    video_client = device_info.get('video_client')
                    if video_client:
                        video_client.disconnect()
                        logging.info(f"Disconnected from video sharing daemon for device {device_index}")
                
                elif device_type == 'shared':
                    # Remove from shared stream server
                    shared_server = device_info.get('shared_server')
                    consumer_id = device_info.get('consumer_id')
                    
                    if shared_server and consumer_id:
                        shared_server.remove_consumer(consumer_id)
                        logging.info(f"Removed consumer from shared stream server for device {device_index}")
            else:
                # Legacy cleanup for old-style streams
                if hasattr(device_info, 'stop'):
                    device_info.stop()
        
        # Clean up video client if exists
        if device_index in self.video_clients:
            video_client = self.video_clients.pop(device_index)
            video_client.disconnect()
            logging.info(f"Cleaned up video sharing client for device {device_index}")
        
        if device_index in self.device_locks:
            del self.device_locks[device_index]
        
        if device_index in self.device_subscribers:
            del self.device_subscribers[device_index]
        
        if device_index in self.device_access_counts:
            del self.device_access_counts[device_index]
    
    def _start_frame_distributor(self, device_index: int):
        """Start a thread to distribute frames to all subscribers."""
        def distribute_frames():
            stream = self.device_streams[device_index]
            
            while stream.running and device_index in self.device_streams:
                try:
                    frame = stream.get_frame()
                    
                    if frame is not None:
                        # Distribute frame to all subscribers
                        with self.device_locks[device_index]:
                            subscribers = self.device_subscribers.get(device_index, {}).copy()
                        
                        for subscriber_id, callback in subscribers.items():
                            try:
                                callback(frame.copy())
                            except Exception as e:
                                logging.error(f"Error calling callback for subscriber {subscriber_id}: {e}")
                    
                    time.sleep(1.0 / 30.0)  # 30 FPS distribution rate
                    
                except Exception as e:
                    logging.error(f"Error in frame distributor for device {device_index}: {e}")
                    time.sleep(0.1)
            
            logging.info(f"Frame distributor for device {device_index} stopped")
        
        distributor_thread = threading.Thread(
            target=distribute_frames,
            name=f"FrameDistributor-{device_index}",
            daemon=True
        )
        distributor_thread.start()
    
    def get_device_info(self, device_index: int) -> Optional[Dict]:
        """Get information about a device."""
        with self.main_lock:
            if device_index not in self.device_streams:
                return None
            
            stream = self.device_streams[device_index]
            return {
                'device_index': device_index,
                'is_connected': stream.is_connected(),
                'state': stream.get_state().value,
                'subscriber_count': self.device_access_counts.get(device_index, 0),
                'subscribers': list(self.device_subscribers.get(device_index, {}).keys())
            }
    
    def get_all_devices_info(self) -> Dict[int, Dict]:
        """Get information about all managed devices."""
        with self.main_lock:
            return {
                device_index: self.get_device_info(device_index)
                for device_index in self.device_streams.keys()
            }
    
    def is_device_available(self, source) -> bool:
        """Check if a direct video device is available."""
        is_device, device_index = self._is_direct_device(source)
        
        if not is_device:
            return False
        
        # Test if device can be opened
        try:
            test_cap = cv2.VideoCapture(device_index)
            available = test_cap.isOpened()
            test_cap.release()
            return available
        except Exception:
            return False
    
    def shutdown(self):
        """Shutdown the manager and clean up all devices."""
        logging.info("Shutting down SharedVideoDeviceManager")
        
        with self.main_lock:
            device_indices = list(self.device_streams.keys())
            
            for device_index in device_indices:
                self._cleanup_device(device_index)
