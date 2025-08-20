import cv2
import random
import logging
import threading
import os

class ImageDebugger:
    """Handles image visualization for AI detections and tracking."""
    def __init__(self, window_name="AI Debugger", display=True):
        """
        Initializes the ImageDebugger.

        :param window_name: Name of the display window.
        :param display: Flag to enable visualization (skips if no GUI available).
        """
        self.window_name = window_name
        self.display = display and os.environ.get("DISPLAY", None) is not None

    def draw_detections(self, frame, detections):
        """
        Draws bounding boxes and labels on the given frame.

        :param frame: The image frame to draw on.
        :param detections: List of detection results.
        :return: Image with drawn detections.
        """
        for detection in detections:
            label = detection.get("label", "unknown")
            confidence = detection.get("confidence", 0)
            bbox = detection.get("bbox", [])

            if not bbox or len(bbox) != 4:
                continue  # Skip invalid bounding boxes

            color = self._get_color(label)
            x1, y1, x2, y2 = map(int, bbox)

            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw label and confidence
            label_text = f"{label} ({confidence:.2f})"
            cv2.putText(frame, label_text, (x1, max(y1 - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return frame

    def draw_tracked_objects(self, frame, tracked_objects):
        """
        Draws tracked objects with unique IDs and attribute matches.

        :param frame: The image frame to draw on.
        :param tracked_objects: List of tracked object results.
        :return: Image with drawn tracking details.
        """
        for obj in tracked_objects:
            track_id = obj.get("track_id", -1)
            detections = obj.get("detections", 0)
            bbox = obj.get("bbox", [])

            if not bbox or len(bbox) != 4:
                continue  # Skip invalid bounding boxes

            color = self._get_color("track")  # Unique color for tracked objects
            x1, y1, x2, y2 = map(int, bbox)

            # Draw tracking box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw track ID and detection count
            track_text = f"ID: {track_id} | Detections: {detections}"
            cv2.putText(frame, track_text, (x1, max(y1 - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Draw attributes
            for attr in obj.get("attributes", []):
                attr_label = attr.get("label", "unknown")
                attr_conf = attr.get("confidence", 0)
                attr_bbox = attr.get("bbox", [])

                if attr_bbox and len(attr_bbox) == 4:
                    ax1, ay1, ax2, ay2 = map(int, attr_bbox)
                    attr_color = self._get_color(attr_label)
                    cv2.rectangle(frame, (ax1, ay1), (ax2, ay2), attr_color, 2)
                    cv2.putText(frame, f"{attr_label} ({attr_conf:.2f})", (ax1, max(ay1 - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, attr_color, 2)

        return frame

    def show_image(self, frame):
        """Displays the image in a window without blocking execution."""
        if self.display:
            print("[DEBUG] Showing image...")  # Debug print
            cv2.imshow(self.window_name, frame)
            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):  # Allows exit with 'q'
                self.close()
            print("[DEBUG] Image displayed.")

    
    def show_image_threaded(self, frame):
        """Runs show_image in a separate thread to prevent blocking."""
        thread = threading.Thread(target=self.show_image, args=(frame,))
        thread.start()

    def save_image(self, frame, filename="debug_output.jpg"):
        """
        Saves the image to a file.

        :param frame: Image to save.
        :param filename: Name of the output file.
        """
        cv2.imwrite(filename, frame)
        logging.info(f"📸 Debug image saved as {filename}")

    def close(self):
        """Closes all OpenCV windows."""
        cv2.destroyAllWindows()
        cv2.waitKey(1)  # Ensure the window fully closes

    def _get_color(self, label):
        """
        Generates a unique color for each label.

        :param label: Label name.
        :return: BGR color tuple.
        """
        random.seed(hash(label) % 256)
        return tuple(random.randint(100, 255) for _ in range(3))
