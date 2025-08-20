import logging
import time
import signal
import os
from pathlib import Path
from typing import Callable, Dict, List, Any, Optional

from .util.DrawingUtils import DrawingUtils
from .streams.VideoStreamManager import VideoStreamManager
from .streams.StreamSyncThread import StreamSyncThread
from .pipeline.PipelineSyncThread import PipelineSyncThread
from .database.DatabaseManager import DatabaseManager
from .services.VideoSharingDaemonManager import get_daemon_manager
from .callbacks import (
    DetectionCallbackManager, 
    DetectionType, 
    CallbackTrigger, 
    DetectionData
)
# Import models to ensure they are registered with SQLAlchemy Base registry
from . import models
import cv2


class CoreService:
    """Service class for running the Nedo Vision Core processing."""

    _callback_manager: Optional[DetectionCallbackManager] = None

    def __init__(self, 
                 drawing_assets_path: str = None,
                 log_level: str = "INFO",
                 storage_path: str = "data",
                 rtmp_server: str = "rtmp://live.vision.sindika.co.id:1935/live",
                 enable_video_sharing_daemon: bool = True):
        """
        Initialize the Core Service.
        
        Args:
            drawing_assets_path: Path to drawing assets directory (optional, uses bundled assets by default)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            storage_path: Storage path for databases and files (default: data)
            rtmp_server: RTMP server URL for video streaming (default: rtmp://localhost:1935/live)
            enable_video_sharing_daemon: Enable automatic video sharing daemon management (default: True)
        """
        self.running = True
        self.video_manager = None
        self.stream_sync_thread = None
        self.pipeline_sync_thread = None
        self.enable_video_sharing_daemon = enable_video_sharing_daemon
        
        # Initialize callback manager if not already done
        if CoreService._callback_manager is None:
            CoreService._callback_manager = DetectionCallbackManager()
        
        # Store configuration parameters
        self.storage_path = storage_path
        self.rtmp_server = rtmp_server
        
        # Use bundled drawing assets by default
        if drawing_assets_path is None:
            # Get the path to the bundled drawing assets
            current_dir = Path(__file__).parent
            self.drawing_assets_path = str(current_dir / "drawing_assets")
        else:
            self.drawing_assets_path = drawing_assets_path
            
        self.log_level = log_level
        
        # Set up logging
        self._setup_logging()
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    # Detection Callback System Methods
    
    @classmethod
    def register_callback(cls,
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
            trigger: When to trigger (ON_NEW_DETECTION or ON_VIOLATION_INTERVAL)
            detection_types: Types of detections to listen for
            interval_seconds: For interval callbacks, how often to call (in seconds)
        
        Example:
            # Immediate callback for PPE violations
            CoreService.register_callback(
                "ppe_alert",
                my_ppe_callback,
                CallbackTrigger.ON_NEW_DETECTION,
                [DetectionType.PPE_DETECTION]
            )
            
            # Interval callback for area violations every 30 seconds
            CoreService.register_callback(
                "area_summary",
                my_area_summary_callback,
                CallbackTrigger.ON_VIOLATION_INTERVAL,
                [DetectionType.AREA_VIOLATION],
                interval_seconds=30
            )
        """
        if cls._callback_manager is None:
            cls._callback_manager = DetectionCallbackManager()
        
        cls._callback_manager.register_callback(
            name=name,
            callback=callback,
            trigger=trigger,
            detection_types=detection_types,
            interval_seconds=interval_seconds
        )
    
    @classmethod
    def unregister_callback(cls, name: str) -> bool:
        """
        Unregister a callback.
        
        Args:
            name: Name of the callback to remove
            
        Returns:
            True if callback was found and removed, False otherwise
        """
        if cls._callback_manager is None:
            return False
        
        return cls._callback_manager.unregister_callback(name)
    
    @classmethod
    def trigger_detection(cls, detection_data: DetectionData) -> None:
        """
        Trigger detection callbacks.
        
        Args:
            detection_data: The detection data to process
        """
        if cls._callback_manager is not None:
            cls._callback_manager.trigger_detection(detection_data)
    
    @classmethod
    def get_callback_stats(cls) -> Dict[str, Any]:
        """
        Get statistics about registered callbacks and recent activity.
        
        Returns:
            Dictionary with callback statistics
        """
        if cls._callback_manager is None:
            return {"error": "Callback manager not initialized"}
        
        return cls._callback_manager.get_callback_stats()
    
    @classmethod
    def list_callbacks(cls) -> Dict[str, Dict[str, Any]]:
        """
        List all callbacks with their configurations.
        
        Returns:
            Dictionary mapping callback names to their configurations
        """
        if cls._callback_manager is None:
            return {}
        
        return cls._callback_manager.list_callbacks()

    def _setup_environment(self):
        """Set up environment variables for components that still require them (like RTMPStreamer)."""
        os.environ["STORAGE_PATH"] = self.storage_path
        os.environ["RTMP_SERVER"] = self.rtmp_server

    def _setup_logging(self):
        """Configure logging settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
        logging.getLogger("pika").setLevel(logging.WARNING)
        logging.getLogger("grpc").setLevel(logging.FATAL)
        logging.getLogger("ffmpeg").setLevel(logging.FATAL)
        logging.getLogger("subprocess").setLevel(logging.FATAL)

    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        logging.info(f"Received signal {signum}, shutting down...")
        self.stop()

    def initialize(self):
        """Initialize all application components."""
        logging.info("🚀 Initializing Nedo Vision Core components...")

        try:
            # Set up environment variables for internal components that still need them
            self._setup_environment()

            # Initialize video sharing daemon manager if enabled
            if self.enable_video_sharing_daemon:
                daemon_manager = get_daemon_manager()
                daemon_manager.enable_auto_start(True)
                logging.info("🔗 Video sharing daemon auto-start enabled")
            else:
                daemon_manager = get_daemon_manager()
                daemon_manager.enable_auto_start(False)
                logging.info("⚠️ Video sharing daemon auto-start disabled")

            # Initialize Database with storage path
            DatabaseManager.init_databases(storage_path=self.storage_path)

            # Initialize Drawing Utils
            DrawingUtils.initialize(self.drawing_assets_path)

            # Initialize Video Stream Manager
            self.video_manager = VideoStreamManager()

            # Start stream synchronization thread
            self.stream_sync_thread = StreamSyncThread(self.video_manager)
            self.stream_sync_thread.start()

            # Start pipeline synchronization thread (AI processing)
            self.pipeline_sync_thread = PipelineSyncThread(self.video_manager)
            self.pipeline_sync_thread.start()

            logging.info("✅ Nedo Vision Core initialized and running.")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to initialize components: {e}", exc_info=True)
            return False

    def run(self):
        """Run the main application loop."""
        if not self.initialize():
            logging.error("❌ Failed to initialize, exiting...")
            return False
            
        try:
            logging.info("🔄 Core service is running. Press Ctrl+C to stop.")
            while self.running:
                time.sleep(1)
            return True
        except KeyboardInterrupt:
            logging.info("🛑 Interrupt received, shutting down...")
            return True
        except Exception as e:
            logging.error(f"❌ Unexpected error: {e}", exc_info=True)
            return False
        finally:
            self.stop()

    def stop(self):
        """Stop all application components gracefully."""
        logging.info("🛑 Stopping Nedo Vision Core...")
        
        self.running = False
        
        try:    
            if self.stream_sync_thread:
                self.stream_sync_thread.running = False
                self.stream_sync_thread.join(timeout=5)
                
            if self.pipeline_sync_thread:
                self.pipeline_sync_thread.running = False
                self.pipeline_sync_thread.join(timeout=5)

            if self.video_manager:
                self.video_manager.stop_all()
            
            # Stop video sharing daemons if they were auto-started
            if self.enable_video_sharing_daemon:
                try:
                    daemon_manager = get_daemon_manager()
                    daemon_manager.stop_all_daemons()
                    logging.info("🔗 Video sharing daemons stopped")
                except Exception as e:
                    logging.warning(f"⚠️ Error stopping video sharing daemons: {e}")
            
            # Stop callback manager
            if CoreService._callback_manager:
                CoreService._callback_manager.stop()
                CoreService._callback_manager = None
                
            # Final cleanup
            cv2.destroyAllWindows()
            for _ in range(5):  # Force windows to close
                cv2.waitKey(1)
                
        except Exception as e:
            logging.error(f"Error during shutdown: {e}")
        finally:
            logging.info("✅ Nedo Vision Core shutdown complete.")