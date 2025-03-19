from picamera2 import Picamera2
from ultralytics import YOLO
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
        self.model = YOLO(model_path) if model_path else None  # Load YOLO model if provided
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
        """Continuously process frames from the queue using the YOLO model."""
        try:
            while self.running:
                if not self.frame_queue.empty():
                    frame = self.frame_queue.get()
                    if self.model:
                        self.process_frame_with_model(frame)
        except KeyboardInterrupt:
            print("Exiting processing thread...")

    def process_frame_with_model(self, frame):
        """
        Process the captured frame using the YOLO model.

        :param frame: The captured frame as a NumPy array.
        """
        # Convert the frame to RGB (if needed by the model)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run the frame through the YOLO model
        results = self.model.predict(source=rgb_frame, conf=0.6, verbose=False)

        # Parse and print the detected objects
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                cls = self.model.names[int(box.cls[0].item())]  # Get class name
                print(f"Detected {cls} with {conf:.2f} confidence at [{x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}]")

# Example usage
if __name__ == "__main__":
    # Pass the YOLO model path as a parameter
    model_path = "yolov5s.pt"  # Ensure this file exists in the working directory
    camera = HeadlessCamera(resolution=(160, 120), frame_rate=30, model_path=model_path)
    camera.start()

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        camera.stop()