import cv2
import threading
import time
from collections import defaultdict

# TODO: fix timer error (because of threading)
class VideoDebugger:
    """Handles real-time visualization of video streams with object detections."""

    def __init__(self, enable_visualization=True):
        """
        Initializes the VideoDebugger with frame drawing and visualization capabilities.

        Args:
            enable_visualization (bool): Whether to display frames.
        """
        self.enable_visualization = enable_visualization
        self.windows = {}  # Tracks OpenCV windows
        self.lock = threading.Lock()  # Thread-safe updates
        self.fps_tracker = defaultdict(lambda: {"start_time": time.time(), "frame_count": 0})

    def show_frame(self, pipeline_id, worker_source_id, frame):
        """
        Displays a frame with FPS overlay.

        Args:
            pipeline_id (str/int): Identifier for the pipeline.
            worker_source_id (str): Identifier for the worker/source.
            frame: The frame to display.
        """
        if not self.enable_visualization or frame is None:
            return

        window_name = f"Pipeline {pipeline_id} - {worker_source_id}"
        with self.lock:
            if window_name not in self.fps_tracker:
                self.fps_tracker[window_name] = {"start_time": time.time(), "frame_count": 0}

            self.fps_tracker[window_name]["frame_count"] += 1
            elapsed_time = time.time() - self.fps_tracker[window_name]["start_time"]
            fps = self.fps_tracker[window_name]["frame_count"] / max(elapsed_time, 1e-5)

            # Display FPS on the frame
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            # Show the window
            if window_name not in self.windows:
                self.windows[window_name] = True  # Register window

            cv2.imshow(window_name, frame)

            # Close on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.close_window(window_name)

    def close_window(self, window_name):
        """Closes a specific OpenCV window."""
        with self.lock:
            if window_name in self.windows:
                cv2.destroyWindow(window_name)
                del self.windows[window_name]

    def close_all(self):
        """Closes all OpenCV windows."""
        with self.lock:
            for window in list(self.windows.keys()):
                cv2.destroyWindow(window)
            self.windows.clear()
        cv2.waitKey(1)
