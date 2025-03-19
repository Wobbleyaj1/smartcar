from picamera2 import Picamera2
import time
import cv2
import threading
import queue

class HeadlessCamera:
    def __init__(self, resolution=(320, 240), frame_rate=30, model_path=None):
        """
        Initialize the HeadlessCamera.

        :param resolution: Tuple specifying the resolution of the camera (width, height).
        :param frame_rate: Integer specifying the frame rate of the camera.
        :param model_path: Path to the YOLO model file (e.g., yolov5s.pt).
        """
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": resolution, "format": "RGB888"}))
        self.picam2.set_controls({"FrameRate": frame_rate})
        self.running = False
        # Commented out YOLO model initialization
        # self.model = YOLO(model_path) if model_path else None
        self.frame_queue = queue.Queue(maxsize=5)  # Queue to hold frames for processing

    def start(self):
        """Start the camera and processing threads."""
        self.picam2.start()
        time.sleep(0.1)  # Allow the camera to warm up
        self.running = True
        print("Camera started")

        # Start the frame capturing thread
        threading.Thread(target=self.capture_frames, daemon=True).start()

        # Start the frame processing thread
        threading.Thread(target=self.process_frames, daemon=True).start()

    def stop(self):
        """Stop the camera."""
        self.running = False
        self.picam2.stop()
        print("Camera stopped")

    def capture_frames(self):
        """Continuously capture frames and add them to the queue."""
        try:
            while self.running:
                if not self.frame_queue.full():
                    frame = self.picam2.capture_array()
                    self.frame_queue.put(frame)
                time.sleep(0.01)  # Small delay to avoid overloading the queue
        except KeyboardInterrupt:
            print("Exiting capture thread...")

    def process_frames(self):
        """Continuously process frames from the queue."""
        try:
            while self.running:
                if not self.frame_queue.empty():
                    frame = self.frame_queue.get()
                    self.process_frame(frame)  # Process the frame
        except KeyboardInterrupt:
            print("Exiting processing thread...")

    def process_frame(self, frame):
        """
        Process the captured frame by printing the color of the middle pixel.

        :param frame: The captured frame as a NumPy array.
        """
        # Get the dimensions of the frame
        height, width, _ = frame.shape

        # Calculate the coordinates of the middle pixel
        mid_x, mid_y = width // 2, height // 2

        # Get the color of the middle pixel (in RGB format)
        middle_pixel_color = frame[mid_y, mid_x]
        print(f"Middle pixel color (RGB): {middle_pixel_color}")

# Example usage
if __name__ == "__main__":
    camera = HeadlessCamera(resolution=(160, 120), frame_rate=30)
    camera.start()

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        camera.stop()