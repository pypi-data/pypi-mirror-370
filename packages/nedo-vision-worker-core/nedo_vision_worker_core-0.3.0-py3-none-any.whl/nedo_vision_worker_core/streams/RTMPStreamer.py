import subprocess
import logging
import cv2
import numpy as np
import os

class RTMPStreamer:
    """Handles streaming video frames to an RTMP server using FFmpeg."""

    def __init__(self, pipeline_id, fps=25, bitrate="1500k"):
        """
        Initializes the RTMP streaming process.

        :param pipeline_id: Unique identifier for the stream (used as the stream key).
        :param fps: Frames per second.
        :param bitrate: Bitrate for video encoding.
        """
        self.rtmp_server = os.environ.get("RTMP_SERVER", "rtmp://localhost:1935/live")
        self.rtmp_url = f"{self.rtmp_server}/{pipeline_id}"  # RTMP URL with dynamic stream key
        self.fps = fps
        self.bitrate = bitrate
        self.width = None
        self.height = None
        self.ffmpeg_process = None
        self.started = False  # Ensure FFmpeg starts only once
        self.active = False  # Add status flag

    def _calculate_resolution(self, frame):
        """Determines resolution with max width 1024 while maintaining aspect ratio."""
        original_height, original_width = frame.shape[:2]
        if original_width > 1024:
            scale_factor = 1024 / original_width
            new_width = 1024
            new_height = int(original_height * scale_factor)
        else:
            new_width, new_height = original_width, original_height

        logging.info(f"📏 Adjusted resolution: {new_width}x{new_height} (Original: {original_width}x{original_height})")
        return new_width, new_height

    def is_active(self):
        """Check if the RTMP streamer is active and ready to send frames."""
        return self.active and self.ffmpeg_process and self.ffmpeg_process.poll() is None

    def _start_ffmpeg_stream(self):
        """Starts an FFmpeg process to stream frames to the RTMP server silently."""
        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-loglevel", "panic",  # 🔇 Suppress all output except fatal errors
            "-nostats",             # 🔇 Hide encoding progress updates
            "-hide_banner",         # 🔇 Hide FFmpeg banner information
            "-f", "rawvideo",
            "-pixel_format", "bgr24",
            "-video_size", f"{self.width}x{self.height}",
            "-framerate", str(self.fps),
            "-i", "-",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-tune", "zerolatency",
            "-b:v", self.bitrate,
            # ❌ Disable Audio (Avoid unnecessary encoding overhead)
            "-an",
            "-maxrate", "2000k",
            "-bufsize", "4000k",
            "-f", "flv",
            self.rtmp_url,
        ]

        try:
            with open(os.devnull, "w") as devnull:
                self.ffmpeg_process = subprocess.Popen(
                    ffmpeg_command,
                    stdin=subprocess.PIPE,
                    stdout=devnull,
                    stderr=devnull
                )
            logging.info(f"📡 RTMP streaming started: {self.rtmp_url} ({self.width}x{self.height})")
            self.started = True
            self.active = True
        except Exception as e:
            logging.error(f"❌ Failed to start FFmpeg: {e}")
            self.ffmpeg_process = None
            self.active = False

    def send_frame(self, frame):
        """Sends a video frame to the RTMP stream with dynamic resolution."""
        if frame is None or not isinstance(frame, np.ndarray):
            logging.error("❌ Invalid frame received")
            return

        try:
            # Validate frame before processing
            if frame.size == 0 or not frame.data:
                logging.error("❌ Empty frame detected")
                return

            # Set resolution on the first frame
            if not self.started:
                self.width, self.height = self._calculate_resolution(frame)
                self._start_ffmpeg_stream()

            if self.is_active():
                # Create a copy of the frame to prevent reference issues
                frame_copy = frame.copy()
                
                # Resize only if necessary
                if frame_copy.shape[1] > 1024:
                    frame_copy = cv2.resize(frame_copy, (self.width, self.height), 
                                         interpolation=cv2.INTER_AREA)

                # Additional frame validation
                if frame_copy.size == 0 or not frame_copy.data:
                    logging.error("❌ Frame became invalid after processing")
                    return

                if self.ffmpeg_process and self.ffmpeg_process.stdin:
                    self.ffmpeg_process.stdin.write(frame_copy.tobytes())
                    self.ffmpeg_process.stdin.flush()  # Ensure data is written

        except BrokenPipeError:
            logging.error("❌ RTMP connection broken")
            self.stop_stream()
        except Exception as e:
            logging.error(f"❌ Failed to send frame to RTMP: {e}")
            self.stop_stream()

    def stop_stream(self):
        """Stops the FFmpeg streaming process."""
        self.active = False
        if self.ffmpeg_process:
            try:
                if self.ffmpeg_process.stdin:
                    self.ffmpeg_process.stdin.close()
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=5)
            except Exception as e:
                logging.error(f"❌ Error stopping RTMP stream: {e}")
                # Force kill if normal termination fails
                try:
                    self.ffmpeg_process.kill()
                except Exception:
                    pass
            finally:
                self.ffmpeg_process = None
                logging.info("✅ RTMP streaming process stopped.")
