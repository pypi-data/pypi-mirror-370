import logging
import time
from .VideoStream import VideoStream
from .SharedVideoDeviceManager import SharedVideoDeviceManager
import threading

class VideoStreamManager:
    """Manages multiple video streams dynamically using VideoStream threads."""

    def __init__(self):
        self.streams = {}  # Store streams as {worker_source_id: VideoStream}
        self.running = False
        self.lock = threading.Lock()  # Add thread lock
        self.shared_device_manager = SharedVideoDeviceManager()
        self.direct_device_streams = {}  # Store direct device streams {worker_source_id: latest_frame}
        self.direct_device_locks = {}  # Store locks for direct device frame access

    def _is_direct_device(self, url) -> bool:
        """Check if URL represents a direct video device."""
        if isinstance(url, str):
            return url.isdigit() or url.startswith('/dev/video')
        return isinstance(url, int)

    def add_stream(self, worker_source_id, url):
        """Adds a new video stream if it's not already active."""
        if worker_source_id not in self.streams and worker_source_id not in self.direct_device_streams:
            # Check if this is a direct video device
            if self._is_direct_device(url):
                self._add_direct_device_stream(worker_source_id, url)
            else:
                # Regular stream (file, RTSP, etc.)
                stream = VideoStream(url)
                stream.start()  # Start the thread
                self.streams[worker_source_id] = stream
                logging.info(f"✅ Added and started video stream: {worker_source_id}")
        else:
            logging.warning(f"⚠️ Stream {worker_source_id} is already active.")

    def _add_direct_device_stream(self, worker_source_id, url):
        """Add a direct device stream using the shared device manager."""
        try:
            # Initialize frame storage for this stream
            self.direct_device_streams[worker_source_id] = {
                'url': url,
                'latest_frame': None,
                'last_update': time.time()
            }
            self.direct_device_locks[worker_source_id] = threading.Lock()
            
            # Create callback for receiving frames
            def frame_callback(frame):
                with self.direct_device_locks[worker_source_id]:
                    self.direct_device_streams[worker_source_id]['latest_frame'] = frame
                    self.direct_device_streams[worker_source_id]['last_update'] = time.time()
            
            # Subscribe to the shared device
            success = self.shared_device_manager.subscribe_to_device(
                source=url,
                subscriber_id=f"stream_{worker_source_id}",
                callback=frame_callback
            )
            
            if success:
                logging.info(f"✅ Added direct device stream: {worker_source_id} -> {url}")
            else:
                # Clean up on failure
                if worker_source_id in self.direct_device_streams:
                    del self.direct_device_streams[worker_source_id]
                if worker_source_id in self.direct_device_locks:
                    del self.direct_device_locks[worker_source_id]
                logging.error(f"❌ Failed to add direct device stream: {worker_source_id}")
                
        except Exception as e:
            logging.error(f"❌ Error adding direct device stream {worker_source_id}: {e}")
            # Clean up on error
            if worker_source_id in self.direct_device_streams:
                del self.direct_device_streams[worker_source_id]
            if worker_source_id in self.direct_device_locks:
                del self.direct_device_locks[worker_source_id]

    def remove_stream(self, worker_source_id):
        """Removes and stops a video stream."""
        if not worker_source_id:
            return

        with self.lock:
            # Check if it's a direct device stream
            if worker_source_id in self.direct_device_streams:
                self._remove_direct_device_stream(worker_source_id)
                return
            
            # Check if it's a regular stream
            if worker_source_id not in self.streams:
                logging.warning(f"⚠️ Stream {worker_source_id} not found in manager.")
                return

            logging.info(f"🛑 Removing video stream: {worker_source_id}")

            # Get reference before removing from dict
            stream = self.streams.pop(worker_source_id, None)

        if stream:
            try:
                stream.stop()

            except Exception as e:
                logging.error(f"❌ Error stopping stream {worker_source_id}: {e}")
            finally:
                stream = None  # Ensure cleanup

        logging.info(f"✅ Stream {worker_source_id} removed successfully.")

    def _remove_direct_device_stream(self, worker_source_id):
        """Remove a direct device stream from the shared device manager."""
        try:
            device_info = self.direct_device_streams.get(worker_source_id)
            if device_info:
                url = device_info['url']
                
                # Unsubscribe from the shared device
                success = self.shared_device_manager.unsubscribe_from_device(
                    source=url,
                    subscriber_id=f"stream_{worker_source_id}"
                )
                
                if success:
                    logging.info(f"✅ Removed direct device stream: {worker_source_id}")
                else:
                    logging.warning(f"⚠️ Failed to unsubscribe direct device stream: {worker_source_id}")
            
            # Clean up local storage
            if worker_source_id in self.direct_device_streams:
                del self.direct_device_streams[worker_source_id]
            if worker_source_id in self.direct_device_locks:
                del self.direct_device_locks[worker_source_id]
                
        except Exception as e:
            logging.error(f"❌ Error removing direct device stream {worker_source_id}: {e}")

    def start_all(self):
        """Starts all video streams."""
        logging.info("🔄 Starting all video streams...")
        for stream in self.streams.values():
            if not stream.is_alive():
                stream.start()  # Start thread if not already running
        self.running = True
    def stop_all(self):
        """Stops all video streams."""
        logging.info("🛑 Stopping all video streams...")
        
        with self.lock:
            # Get a list of IDs to avoid modification during iteration
            stream_ids = list(self.streams.keys())
            direct_stream_ids = list(self.direct_device_streams.keys())
            
        # Stop each regular stream
        for worker_source_id in stream_ids:
            try:
                self.remove_stream(worker_source_id)
            except Exception as e:
                logging.error(f"Error stopping stream {worker_source_id}: {e}")
        
        # Stop each direct device stream
        for worker_source_id in direct_stream_ids:
            try:
                self.remove_stream(worker_source_id)
            except Exception as e:
                logging.error(f"Error stopping direct device stream {worker_source_id}: {e}")
        
        self.running = False

    def get_frame(self, worker_source_id):
        """Retrieves the latest frame for a specific stream."""
        # Check if it's a direct device stream first
        if worker_source_id in self.direct_device_streams:
            return self._get_direct_device_frame(worker_source_id)
        
        # Handle regular streams
        with self.lock:  # Add lock protection for stream access
            stream = self.streams.get(worker_source_id)
            if stream is None:
                return None

            # Check if stream is still running
            if not stream.running:
                return None

            try:
                # **Ignore warnings for the first 5 seconds**
                elapsed_time = time.time() - stream.start_time
                if elapsed_time < 5:
                    return None

                # Check if video file has ended
                if stream.is_file and stream.is_video_ended():
                    logging.debug(f"Video file {worker_source_id} has ended, waiting for restart...")
                    # Small delay to allow the video to restart
                    time.sleep(0.1)
                    return None

                return stream.get_frame()  # Already returns a copy
            except Exception as e:
                logging.error(f"Error getting frame from stream {worker_source_id}: {e}")
                return None

    def _get_direct_device_frame(self, worker_source_id):
        """Get the latest frame from a direct device stream."""
        try:
            if worker_source_id not in self.direct_device_locks:
                return None
            
            with self.direct_device_locks[worker_source_id]:
                device_info = self.direct_device_streams.get(worker_source_id)
                if not device_info:
                    return None
                
                frame = device_info.get('latest_frame')
                last_update = device_info.get('last_update', 0)
                
                # Check if frame is too old (5 seconds threshold)
                if time.time() - last_update > 5.0:
                    return None
                
                return frame.copy() if frame is not None else None
                
        except Exception as e:
            logging.error(f"Error getting frame from direct device stream {worker_source_id}: {e}")
            return None

    def get_active_stream_ids(self):
        """Returns a list of active stream IDs."""
        regular_streams = list(self.streams.keys())
        direct_streams = list(self.direct_device_streams.keys())
        return regular_streams + direct_streams

    def get_stream_url(self, worker_source_id):
        """Returns the URL of a specific stream."""
        # Check direct device streams first
        if worker_source_id in self.direct_device_streams:
            return self.direct_device_streams[worker_source_id]['url']
        
        # Check regular streams
        stream = self.streams.get(worker_source_id)
        return stream.source if stream else None
    
    def has_stream(self, worker_source_id):
        """Checks if a stream is active."""
        return (worker_source_id in self.streams or 
                worker_source_id in self.direct_device_streams)

    def is_running(self):
        """Checks if the manager is running."""
        return self.running

    def is_video_file(self, worker_source_id):
        """Check if a stream is a video file."""
        # Direct device streams are never video files
        if worker_source_id in self.direct_device_streams:
            return False
        
        # Check regular streams
        stream = self.streams.get(worker_source_id)
        return stream.is_file if stream else False

    def get_device_sharing_info(self):
        """Get information about device sharing."""
        return self.shared_device_manager.get_all_devices_info()

    def shutdown(self):
        """Shutdown the manager and clean up all resources."""
        logging.info("Shutting down VideoStreamManager")
        self.stop_all()
        # The SharedVideoDeviceManager is a singleton and will clean up automatically
