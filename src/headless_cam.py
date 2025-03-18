from picamera2 import Picamera2
from ultralytics import YOLO
import time
import cv2

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

    def start(self):
        """Start the camera."""
        self.picam2.start()
        time.sleep(0.1)  # Allow the camera to warm up
        self.running = True
        print("Camera started")

    def stop(self):
        """Stop the camera."""
        self.picam2.stop()
        self.running = False
        print("Camera stopped")

    def capture_frames(self):
        """Capture frames in a loop."""
        try:
            while self.running:
                # Capture a frame
                frame = self.picam2.capture_array()

                # Process the frame using the YOLO model (if provided)
                if self.model:
                    self.process_frame_with_model(frame)

                # Add a small delay to simulate processing time
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            self.stop()

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
    camera = HeadlessCamera(resolution=(320, 240), frame_rate=30, model_path=model_path)
    camera.start()
    camera.capture_frames()