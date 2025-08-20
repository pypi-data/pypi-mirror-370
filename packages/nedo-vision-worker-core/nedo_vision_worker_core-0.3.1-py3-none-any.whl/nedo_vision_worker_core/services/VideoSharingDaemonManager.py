"""
Video Sharing Daemon Manager for automatic daemon lifecycle management.
"""

import logging
import threading
import time
import os
import json
from pathlib import Path
import tempfile
from typing import Dict, Optional, Set
from .VideoSharingDaemon import VideoSharingDaemon
from ..database.DatabaseManager import DatabaseManager


class VideoSharingDaemonManager:
    """
    Manages video sharing daemons for multiple devices automatically.
    Integrates with CoreService to start/stop daemons as needed.
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
        self.daemons = {}  # Dict[int, VideoSharingDaemon]
        self.daemon_threads: Dict[int, threading.Thread] = {}
        self.managed_devices: Set[int] = set()
        self.running = False
        self.auto_start_enabled = True
        
        logging.info("🔗 VideoSharingDaemonManager initialized")
    
    def enable_auto_start(self, enabled: bool = True):
        """Enable or disable automatic daemon starting."""
        self.auto_start_enabled = enabled
        logging.info(f"📋 Auto-start video sharing daemons: {'enabled' if enabled else 'disabled'}")
    
    def is_daemon_running(self, device_index: int) -> bool:
        """Check if daemon is running for a specific device."""
        if not VideoSharingDaemon:
            return False
            
        try:
            # Get storage path from DatabaseManager
            storage_path = None
            if DatabaseManager and hasattr(DatabaseManager, 'STORAGE_PATH') and DatabaseManager.STORAGE_PATH:
                storage_path = str(DatabaseManager.STORAGE_PATH)
            
            # Use the same socket path logic as the daemon
            from nedo_vision_worker_core.services.VideoSharingDaemon import get_storage_socket_path
            socket_path = get_storage_socket_path(device_index, storage_path)
            info_file = socket_path.parent / f"vd{device_index}_info.json"
            
            if info_file.exists():
                with open(info_file, 'r') as f:
                    info = json.load(f)
                
                pid = info.get('pid')
                if pid:
                    try:
                        # Cross-platform process check
                        import platform
                        if platform.system() == 'Windows':
                            import subprocess
                            result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                                  capture_output=True, text=True)
                            return str(pid) in result.stdout
                        else:
                            os.kill(pid, 0)  # Check if process exists
                            return True
                    except (OSError, ProcessLookupError, subprocess.SubprocessError):
                        # Process is dead, clean up
                        info_file.unlink()
        except Exception:
            pass
        return False
    
    def start_daemon_for_device(self, device_index: int) -> bool:
        """Start a video sharing daemon for a specific device."""
        if not VideoSharingDaemon:
            logging.warning(f"Video sharing daemon not available, cannot start daemon for device {device_index}")
            return False
            
        if device_index in self.daemons:
            logging.info(f"📹 Daemon for device {device_index} already managed")
            return True
            
        # Check if external daemon is already running
        if self.is_daemon_running(device_index):
            logging.info(f"📹 External daemon for device {device_index} already running")
            return True
        
        try:
            # Get storage path from DatabaseManager
            storage_path = None
            if DatabaseManager and hasattr(DatabaseManager, 'STORAGE_PATH') and DatabaseManager.STORAGE_PATH:
                storage_path = str(DatabaseManager.STORAGE_PATH)
            
            # Create daemon instance
            daemon = VideoSharingDaemon(device_index, storage_path=storage_path)
            
            # Start daemon in separate thread
            def daemon_runner():
                try:
                    logging.info(f"🚀 Starting video sharing daemon for device {device_index}")
                    daemon.start_daemon()
                except Exception as e:
                    logging.error(f"❌ Error running daemon for device {device_index}: {e}")
                finally:
                    # Clean up when daemon stops
                    with self._lock:
                        if device_index in self.daemons:
                            del self.daemons[device_index]
                        if device_index in self.daemon_threads:
                            del self.daemon_threads[device_index]
                        if device_index in self.managed_devices:
                            self.managed_devices.remove(device_index)
            
            daemon_thread = threading.Thread(
                target=daemon_runner,
                name=f"VideoSharingDaemon-{device_index}",
                daemon=True
            )
            
            # Store references
            self.daemons[device_index] = daemon
            self.daemon_threads[device_index] = daemon_thread
            self.managed_devices.add(device_index)
            
            # Start the daemon
            daemon_thread.start()
            
            # Give daemon time to start
            time.sleep(1)
            
            # Verify daemon started successfully
            if self.is_daemon_running(device_index):
                logging.info(f"✅ Video sharing daemon started for device {device_index}")
                return True
            else:
                logging.error(f"❌ Failed to start video sharing daemon for device {device_index}")
                self.stop_daemon_for_device(device_index)
                return False
                
        except Exception as e:
            logging.error(f"❌ Error starting daemon for device {device_index}: {e}")
            return False
    
    def stop_daemon_for_device(self, device_index: int):
        """Stop the video sharing daemon for a specific device."""
        try:
            if device_index in self.daemons:
                daemon = self.daemons[device_index]
                logging.info(f"🛑 Stopping video sharing daemon for device {device_index}")
                daemon.stop_daemon()
                
                # Wait for thread to finish
                if device_index in self.daemon_threads:
                    thread = self.daemon_threads[device_index]
                    thread.join(timeout=5)
                
                # Clean up references
                if device_index in self.daemons:
                    del self.daemons[device_index]
                if device_index in self.daemon_threads:
                    del self.daemon_threads[device_index]
                if device_index in self.managed_devices:
                    self.managed_devices.remove(device_index)
                
                logging.info(f"✅ Video sharing daemon stopped for device {device_index}")
                
        except Exception as e:
            logging.error(f"❌ Error stopping daemon for device {device_index}: {e}")
    
    def ensure_daemon_for_device(self, device_index: int) -> bool:
        """
        Ensure a daemon is running for the device. 
        Start one if auto-start is enabled and none is running.
        """
        if not self.auto_start_enabled:
            return self.is_daemon_running(device_index)
            
        # Check if daemon is already running (managed or external)
        if self.is_daemon_running(device_index):
            return True
            
        # Try to start our own daemon
        return self.start_daemon_for_device(device_index)
    
    def start_all_managed_daemons(self):
        """Start daemons for all currently managed devices."""
        self.running = True
        for device_index in list(self.managed_devices):
            if not self.is_daemon_running(device_index):
                self.start_daemon_for_device(device_index)
    
    def stop_all_daemons(self):
        """Stop all managed video sharing daemons."""
        logging.info("🛑 Stopping all video sharing daemons...")
        self.running = False
        
        # Stop all managed daemons
        device_indices = list(self.managed_devices)
        for device_index in device_indices:
            self.stop_daemon_for_device(device_index)
        
        logging.info("✅ All video sharing daemons stopped")
    
    def get_daemon_status(self) -> Dict[int, Dict]:
        """Get status of all managed daemons."""
        status = {}
        
        for device_index in self.managed_devices:
            is_running = self.is_daemon_running(device_index)
            thread_alive = device_index in self.daemon_threads and self.daemon_threads[device_index].is_alive()
            
            status[device_index] = {
                'managed': True,
                'daemon_running': is_running,
                'thread_alive': thread_alive,
                'auto_start': self.auto_start_enabled
            }
        
        return status
    
    def get_device_info(self, device_index: int) -> Optional[Dict]:
        """Get device information from daemon if available."""
        try:
            info_file = Path(tempfile.gettempdir()) / f"video_device_{device_index}_info.json"
            if info_file.exists():
                with open(info_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return None


# Singleton instance
daemon_manager = VideoSharingDaemonManager()


def get_daemon_manager() -> VideoSharingDaemonManager:
    """Get the singleton daemon manager instance."""
    return daemon_manager
