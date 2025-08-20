#!/usr/bin/env python3
"""
Cross-Platform Video Sharing Daemon - A system-wide service that captures from a video device
and shares frames with multiple consumers across different processes.

Supports Windows (Named Pipes), Linux/macOS (Unix Domain Sockets), and fallback TCP.
"""

import cv2
import numpy as np
import socket
import struct
import threading
import time
import logging
import json
import os
import sys
import platform
from pathlib import Path
import tempfile
from ..database.DatabaseManager import DatabaseManager
from abc import ABC, abstractmethod

# Platform-specific imports
if platform.system() == 'Windows':
    try:
        import win32pipe
        import win32file
        import win32api
        import win32con
        import pywintypes
        WINDOWS_SUPPORT = True
    except ImportError:
        WINDOWS_SUPPORT = False
        logging.warning("pywin32 not available, falling back to TCP sockets")
else:
    import signal
    WINDOWS_SUPPORT = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_storage_socket_path(device_index, storage_path=None):
    """Get storage-based socket path for video sharing daemon with length optimization."""
    try:
        if storage_path:
            # Use explicitly provided storage path
            socket_dir = Path(storage_path) / "sockets"
        elif DatabaseManager and hasattr(DatabaseManager, 'STORAGE_PATH') and DatabaseManager.STORAGE_PATH:
            # Use storage path from DatabaseManager if available
            socket_dir = DatabaseManager.STORAGE_PATH / "sockets"
        else:
            # Fallback to temp directory with short path
            return Path(tempfile.gettempdir()) / f"nvw_vd{device_index}.sock"
        
        socket_dir.mkdir(parents=True, exist_ok=True)
        socket_path = socket_dir / f"vd{device_index}.sock"
        
        # Check if the path is too long for Unix domain sockets (limit ~100-108 chars)
        if len(str(socket_path)) > 100:
            # Try to use a shorter path by using relative path from current directory
            try:
                relative_path = socket_path.relative_to(Path.cwd())
                if len(str(relative_path)) < len(str(socket_path)):
                    socket_path = relative_path
            except ValueError:
                # If relative path doesn't work, use temp directory fallback
                logging.warning(f"Socket path too long ({len(str(socket_path))} chars), using temp directory")
                return Path(tempfile.gettempdir()) / f"nvw_vd{device_index}.sock"
        
        return socket_path
        
    except Exception as e:
        logging.debug(f"Could not use storage path: {e}")
        # Fallback to temp directory with short path
        return Path(tempfile.gettempdir()) / f"nvw_vd{device_index}.sock"


class IPCBackend(ABC):
    """Abstract base class for IPC backends."""
    
    @abstractmethod
    def create_server(self, address):
        """Create and return a server socket/pipe."""
        pass
    
    @abstractmethod
    def accept_client(self, server):
        """Accept a client connection."""
        pass
    
    @abstractmethod
    def connect_client(self, address):
        """Connect as a client."""
        pass
    
    @abstractmethod
    def send_data(self, connection, data):
        """Send data through connection."""
        pass
    
    @abstractmethod
    def receive_data(self, connection, size):
        """Receive data from connection."""
        pass
    
    @abstractmethod
    def close_connection(self, connection):
        """Close a connection."""
        pass
    
    @abstractmethod
    def close_server(self, server):
        """Close server and cleanup."""
        pass


class UnixSocketBackend(IPCBackend):
    """Unix Domain Socket backend for Linux/macOS."""
    
    def __init__(self):
        self.socket_paths = {}
    
    def create_server(self, address):
        """Create Unix domain socket server."""
        # Remove existing socket file
        try:
            os.unlink(address)
        except OSError:
            pass
        
        server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_socket.bind(address)
        server_socket.listen(10)
        self.socket_paths[server_socket] = address
        return server_socket
    
    def accept_client(self, server):
        """Accept client connection."""
        return server.accept()[0]
    
    def connect_client(self, address):
        """Connect as client."""
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client_socket.connect(address)
        return client_socket
    
    def send_data(self, connection, data):
        """Send data through socket."""
        connection.sendall(data)
    
    def receive_data(self, connection, size):
        """Receive data from socket."""
        data = b''
        while len(data) < size:
            chunk = connection.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def close_connection(self, connection):
        """Close socket connection."""
        try:
            connection.close()
        except:
            pass
    
    def close_server(self, server):
        """Close server and cleanup socket file."""
        try:
            socket_path = self.socket_paths.get(server)
            server.close()
            if socket_path:
                os.unlink(socket_path)
                del self.socket_paths[server]
        except:
            pass


class NamedPipeBackend(IPCBackend):
    """Named Pipe backend for Windows."""
    
    def __init__(self):
        self.pipe_names = {}
    
    def create_server(self, address):
        """Create named pipe server."""
        pipe_name = f"\\\\.\\pipe\\{address}"
        self.pipe_names[pipe_name] = address
        return pipe_name
    
    def accept_client(self, server):
        """Accept client connection on named pipe."""
        try:
            # Create named pipe
            pipe_handle = win32pipe.CreateNamedPipe(
                server,
                win32pipe.PIPE_ACCESS_DUPLEX,
                win32pipe.PIPE_TYPE_BYTE | win32pipe.PIPE_READMODE_BYTE | win32pipe.PIPE_WAIT,
                win32pipe.PIPE_UNLIMITED_INSTANCES,
                65536,  # Output buffer size
                65536,  # Input buffer size
                0,      # Default timeout
                None    # Default security
            )
            
            # Wait for client connection
            win32pipe.ConnectNamedPipe(pipe_handle, None)
            return pipe_handle
            
        except pywintypes.error as e:
            logging.error(f"Error creating named pipe: {e}")
            return None
    
    def connect_client(self, address):
        """Connect as client to named pipe."""
        pipe_name = f"\\\\.\\pipe\\{address}"
        try:
            pipe_handle = win32file.CreateFile(
                pipe_name,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            return pipe_handle
        except pywintypes.error as e:
            logging.error(f"Error connecting to named pipe: {e}")
            return None
    
    def send_data(self, connection, data):
        """Send data through named pipe."""
        try:
            win32file.WriteFile(connection, data)
        except pywintypes.error as e:
            raise ConnectionError(f"Failed to send data: {e}")
    
    def receive_data(self, connection, size):
        """Receive data from named pipe."""
        try:
            data = b''
            while len(data) < size:
                result, chunk = win32file.ReadFile(connection, size - len(data))
                if not chunk:
                    return None
                data += chunk
            return data
        except pywintypes.error as e:
            logging.error(f"Error reading from named pipe: {e}")
            return None
    
    def close_connection(self, connection):
        """Close named pipe connection."""
        try:
            win32file.CloseHandle(connection)
        except:
            pass
    
    def close_server(self, server):
        """Close named pipe server."""
        # Named pipe servers are handled per-connection
        pass


class TCPSocketBackend(IPCBackend):
    """TCP Socket backend (fallback for all platforms)."""
    
    def __init__(self):
        self.base_port = 19000
        self.port_map = {}
    
    def create_server(self, address):
        """Create TCP server socket."""
        # Convert address to port number
        port = self.base_port + hash(address) % 1000
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('127.0.0.1', port))
        server_socket.listen(10)
        
        self.port_map[server_socket] = port
        logging.info(f"TCP server listening on 127.0.0.1:{port}")
        return server_socket
    
    def accept_client(self, server):
        """Accept client connection."""
        return server.accept()[0]
    
    def connect_client(self, address):
        """Connect as TCP client."""
        port = self.base_port + hash(address) % 1000
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', port))
        return client_socket
    
    def send_data(self, connection, data):
        """Send data through TCP socket."""
        connection.sendall(data)
    
    def receive_data(self, connection, size):
        """Receive data from TCP socket."""
        data = b''
        while len(data) < size:
            chunk = connection.recv(size - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def close_connection(self, connection):
        """Close TCP connection."""
        try:
            connection.close()
        except:
            pass
    
    def close_server(self, server):
        """Close TCP server."""
        try:
            server.close()
            if server in self.port_map:
                del self.port_map[server]
        except:
            pass


class VideoSharingDaemon:
    """Video sharing daemon with automatic platform detection."""
    
    def __init__(self, device_index=0, backend=None, storage_path=None):
        self.device_index = device_index
        self.socket_path = get_storage_socket_path(device_index, storage_path)
        self.address = str(self.socket_path) if backend != 'tcp' else f"video_share_device_{device_index}"
        self.info_file = self.socket_path.parent / f"vd{device_index}_info.json"
        
        # Select IPC backend
        self.backend = self._select_backend(backend)
        
        self.cap = None
        self.running = False
        self.clients = []
        self.clients_lock = threading.Lock()
        
        # Video properties
        self.width = 640
        self.height = 480
        self.fps = 30.0
        
        # Server
        self.server = None
        
    def _select_backend(self, backend=None):
        """Select appropriate IPC backend."""
        if backend:
            return backend
        
        system = platform.system()
        
        if system == 'Windows' and WINDOWS_SUPPORT:
            logging.info("🖥️ Using Named Pipes backend (Windows)")
            return NamedPipeBackend()
        elif system in ['Linux', 'Darwin'] and hasattr(socket, 'AF_UNIX'):
            logging.info(f"🐧 Using Unix Domain Sockets backend ({system})")
            return UnixSocketBackend()
        else:
            logging.info("🌐 Using TCP Socket backend (fallback)")
            return TCPSocketBackend()
    
    def start_daemon(self):
        """Start the video sharing daemon."""
        try:
            # Check if daemon is already running
            if self._is_daemon_running():
                logging.error(f"Video sharing daemon for device {self.device_index} is already running")
                return False
            
            # Open video device
            self.cap = cv2.VideoCapture(self.device_index)
            if not self.cap.isOpened():
                logging.error(f"Cannot open video device {self.device_index}")
                return False
            
            # Get device properties
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = float(self.cap.get(cv2.CAP_PROP_FPS))
            
            if self.fps <= 0:
                self.fps = 30.0
            
            logging.info(f"📹 Device {self.device_index} opened: {self.width}x{self.height} @ {self.fps}fps")
            
            # Create server
            self.server = self.backend.create_server(self.address)
            
            # Write daemon info file
            self._write_daemon_info()
            
            # Start capture and server threads
            self.running = True
            
            capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            server_thread = threading.Thread(target=self._server_loop, daemon=True)
            
            capture_thread.start()
            server_thread.start()
            
            logging.info(f"🚀 Video sharing daemon started for device {self.device_index}")
            
            # Setup shutdown handlers
            self._setup_shutdown_handlers()
            
            # Keep daemon running
            while self.running:
                time.sleep(1)
                
            return True
            
        except Exception as e:
            logging.error(f"Failed to start daemon: {e}")
            self.stop_daemon()
            return False
    
    def _setup_shutdown_handlers(self):
        """Setup platform-appropriate shutdown handlers."""
        try:
            if platform.system() == 'Windows':
                # Windows console control handler
                if WINDOWS_SUPPORT:
                    try:
                        def ctrl_handler(ctrl_type):
                            if ctrl_type in (win32con.CTRL_C_EVENT, win32con.CTRL_CLOSE_EVENT):
                                logging.info("Received shutdown signal...")
                                self.stop_daemon()
                                return True
                            return False
                        
                        win32api.SetConsoleCtrlHandler(ctrl_handler, True)
                        logging.info("📡 Windows console control handler registered")
                    except Exception as e:
                        logging.warning(f"Could not set up Windows control handler: {e}")
            else:
                # Unix signal handlers (only in main thread)
                if threading.current_thread() is threading.main_thread():
                    signal.signal(signal.SIGTERM, self._signal_handler)
                    signal.signal(signal.SIGINT, self._signal_handler)
                    logging.info("📡 Signal handlers registered (main thread)")
                else:
                    logging.info("⚠️ Skipping signal handlers (not main thread)")
        except Exception as e:
            logging.warning(f"⚠️ Could not set up shutdown handlers: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle Unix signals."""
        logging.info(f"Received signal {signum}, shutting down...")
        self.stop_daemon()
    
    def _is_daemon_running(self):
        """Check if daemon is already running for this device."""
        try:
            if self.info_file.exists():
                with open(self.info_file, 'r') as f:
                    info = json.load(f)
                
                pid = info.get('pid')
                if pid:
                    try:
                        if platform.system() == 'Windows':
                            # Windows process check
                            import subprocess
                            result = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], 
                                                  capture_output=True, text=True)
                            return str(pid) in result.stdout
                        else:
                            # Unix process check
                            os.kill(pid, 0)
                            return True
                    except (OSError, ProcessLookupError, subprocess.SubprocessError):
                        # Process is dead, clean up
                        self.info_file.unlink()
        except Exception:
            pass
        return False
    
    def _write_daemon_info(self):
        """Write daemon information to file."""
        info = {
            'device_index': self.device_index,
            'pid': os.getpid(),
            'address': self.address,
            'backend': self.backend.__class__.__name__,
            'platform': platform.system(),
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'started_at': time.time()
        }
        
        with open(self.info_file, 'w') as f:
            json.dump(info, f)
    
    def _server_loop(self):
        """Accept and handle client connections."""
        while self.running:
            try:
                client = self.backend.accept_client(self.server)
                if client:
                    logging.info(f"📱 New client connected")
                    
                    with self.clients_lock:
                        self.clients.append(client)
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client, 
                        args=(client,), 
                        daemon=True
                    )
                    client_thread.start()
                
            except Exception as e:
                if self.running:
                    logging.error(f"Error accepting client: {e}")
    
    def _handle_client(self, client):
        """Handle individual client connection."""
        try:
            while self.running:
                # Keep connection alive
                time.sleep(1)
        except Exception as e:
            logging.warning(f"Client disconnected: {e}")
        finally:
            with self.clients_lock:
                if client in self.clients:
                    self.clients.remove(client)
            self.backend.close_connection(client)
    
    def _capture_loop(self):
        """Main video capture loop."""
        frame_interval = 1.0 / self.fps
        last_frame_time = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Throttle frame rate
                if current_time - last_frame_time < frame_interval:
                    time.sleep(0.001)
                    continue
                
                ret, frame = self.cap.read()
                if not ret:
                    logging.warning("Failed to read frame")
                    time.sleep(0.1)
                    continue
                
                # Broadcast frame to all clients
                self._broadcast_frame(frame)
                
                last_frame_time = current_time
                
            except Exception as e:
                logging.error(f"Error in capture loop: {e}")
                time.sleep(0.1)
    
    def _broadcast_frame(self, frame):
        """Broadcast frame to all connected clients."""
        if not self.clients:
            return
        
        try:
            # Serialize frame
            frame_data = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])[1].tobytes()
            frame_size = len(frame_data)
            
            # Prepare message: [size][width][height][timestamp][frame_data]
            message = struct.pack('!IIIf', frame_size, self.width, self.height, time.time())
            message += frame_data
            
            with self.clients_lock:
                dead_clients = []
                
                for client in self.clients:
                    try:
                        self.backend.send_data(client, message)
                    except Exception as e:
                        dead_clients.append(client)
                
                # Remove dead clients
                for client in dead_clients:
                    self.clients.remove(client)
                    self.backend.close_connection(client)
                
        except Exception as e:
            logging.error(f"Error broadcasting frame: {e}")
    
    def stop_daemon(self):
        """Stop the video sharing daemon."""
        logging.info("🛑 Stopping video sharing daemon...")
        
        self.running = False
        
        # Close all client connections
        with self.clients_lock:
            for client in self.clients:
                self.backend.close_connection(client)
            self.clients.clear()
        
        # Close server
        if self.server:
            self.backend.close_server(self.server)
        
        # Close video capture
        if self.cap:
            self.cap.release()
        
        # Clean up info file
        try:
            self.info_file.unlink()
        except:
            pass
        
        logging.info("✅ Video sharing daemon stopped")


class VideoSharingClient:
    """Video sharing client with automatic platform detection."""
    
    def __init__(self, device_index=0, backend=None, storage_path=None):
        self.device_index = device_index
        self.socket_path = get_storage_socket_path(device_index, storage_path)
        self.address = str(self.socket_path) if backend != 'tcp' else f"video_share_device_{device_index}"
        self.info_file = self.socket_path.parent / f"vd{device_index}_info.json"
        
        # Backend will be determined from daemon info
        self.backend = backend
        self.connection = None
        self.running = False
        self.frame_callback = None
        
        # Device properties
        self.width = 640
        self.height = 480
        self.fps = 30.0
    
    def connect(self, frame_callback):
        """Connect to video sharing daemon."""
        try:
            # Check if daemon is running and get info
            if not self._load_daemon_info():
                logging.error(f"Video sharing daemon for device {self.device_index} is not running")
                return False
            
            # Create appropriate backend if not provided
            if not self.backend:
                self.backend = self._create_backend_from_info()
            
            # Connect to daemon
            self.connection = self.backend.connect_client(self.address)
            if not self.connection:
                return False
            
            self.frame_callback = frame_callback
            self.running = True
            
            # Start receiving thread
            receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            receive_thread.start()
            
            logging.info(f"📱 Connected to video sharing daemon for device {self.device_index}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to connect to daemon: {e}")
            return False
    
    def _load_daemon_info(self):
        """Load daemon information from file."""
        try:
            if not self.info_file.exists():
                return False
            
            with open(self.info_file, 'r') as f:
                info = json.load(f)
            
            self.width = info['width']
            self.height = info['height']
            self.fps = info['fps']
            self.daemon_platform = info.get('platform', platform.system())
            self.daemon_backend = info.get('backend', 'UnixSocketBackend')
            
            return True
            
        except Exception as e:
            logging.error(f"Error loading daemon info: {e}")
            return False
    
    def _create_backend_from_info(self):
        """Create backend based on daemon info."""
        if self.daemon_backend == 'NamedPipeBackend':
            return NamedPipeBackend()
        elif self.daemon_backend == 'UnixSocketBackend':
            return UnixSocketBackend()
        else:
            return TCPSocketBackend()
    
    def _receive_loop(self):
        """Receive frames from daemon."""
        while self.running:
            try:
                # Receive header: [size][width][height][timestamp]
                header = self.backend.receive_data(self.connection, 16)  # 4 + 4 + 4 + 4 bytes
                if not header:
                    break
                
                frame_size, width, height, timestamp = struct.unpack('!IIIf', header)
                
                # Receive frame data
                frame_data = self.backend.receive_data(self.connection, frame_size)
                if not frame_data:
                    break
                
                # Decode frame
                frame_array = np.frombuffer(frame_data, dtype=np.uint8)
                frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
                
                if frame is not None and self.frame_callback:
                    self.frame_callback(frame, timestamp)
                
            except Exception as e:
                if self.running:
                    logging.error(f"Error receiving frame: {e}")
                break
    
    def disconnect(self):
        """Disconnect from daemon."""
        self.running = False
        if self.connection and self.backend:
            self.backend.close_connection(self.connection)
        logging.info("📱 Disconnected from video sharing daemon")
    
    def get_device_properties(self):
        """Get device properties."""
        return self.width, self.height, self.fps, "bgr24"


def main():
    """Main function to run daemon or test client."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Video Sharing Daemon')
    parser.add_argument('--device', type=int, default=0, help='Video device index')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--test-client', action='store_true', help='Test client mode')
    parser.add_argument('--backend', choices=['unix', 'namedpipe', 'tcp'], 
                       help='Force specific backend')
    
    args = parser.parse_args()
    
    # Create backend if specified
    backend = None
    if args.backend:
        if args.backend == 'unix':
            backend = UnixSocketBackend()
        elif args.backend == 'namedpipe':
            backend = NamedPipeBackend()
        elif args.backend == 'tcp':
            backend = TCPSocketBackend()
    
    if args.daemon:
        # Run as daemon
        daemon = VideoSharingDaemon(args.device, backend)
        daemon.start_daemon()
    elif args.test_client:
        # Test client
        def on_frame(frame, timestamp):
            print(f"📹 Received frame: {frame.shape}, timestamp: {timestamp}")
        
        client = VideoSharingClient(args.device, backend)
        if client.connect(on_frame):
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                client.disconnect()
    else:
        system = platform.system()
        backend_info = "Named Pipes" if system == 'Windows' and WINDOWS_SUPPORT else \
                      "Unix Domain Sockets" if hasattr(socket, 'AF_UNIX') else "TCP Sockets"
        
        print(f"Video Sharing Daemon")
        print(f"Platform: {system}")
        print(f"IPC Backend: {backend_info}")
        print(f"Usage: python {sys.argv[0]} --daemon  OR  --test-client")
        
        if system == 'Windows' and not WINDOWS_SUPPORT:
            print("Note: Install pywin32 for optimal Windows support (pip install pywin32)")


if __name__ == "__main__":
    main()
