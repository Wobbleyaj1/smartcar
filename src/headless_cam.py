from picamera2 import Picamera2
import time
import cv2
import threading
import queue
import onnxruntime as ort
import numpy as np

class HeadlessCamera:
    def __init__(self, resolution=(320, 240), frame_rate=30, model_path=None):
        """
        Initialize the HeadlessCamera.

        :param resolution: Tuple specifying the resolution of the camera (width, height).
        :param frame_rate: Integer specifying the frame rate of the camera.
        :param model_path: Path to the ONNX model file (e.g., yolov5s.onnx).
        """
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": resolution, "format": "RGB888"}))
        self.picam2.set_controls({"FrameRate": frame_rate})
        self.running = False
        self.frame_queue = queue.Queue(maxsize=5)  # Queue to hold frames for processing

        # Load the ONNX model
        if model_path:
            self.session = ort.InferenceSession(model_path)
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
        else:
            self.session = None

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
        Process the captured frame using the ONNX model or print the middle pixel color.

        :param frame: The captured frame as a NumPy array.
        """
        if self.session:
            # Preprocess the frame for ONNX model
            input_tensor = self.preprocess_frame(frame)

            # Run inference
            outputs = self.session.run([self.output_name], {self.input_name: input_tensor})

            # Post-process and print detected objects
            self.postprocess_and_print(outputs, frame)
        else:
            # Get the dimensions of the frame
            height, width, _ = frame.shape

            # Calculate the coordinates of the middle pixel
            mid_x, mid_y = width // 2, height // 2

            # Get the color of the middle pixel (in RGB format)
            middle_pixel_color = frame[mid_y, mid_x]
            print(f"Middle pixel color (RGB): {middle_pixel_color}")

    def preprocess_frame(self, frame):
        """Preprocess the frame for ONNX model inference."""
        resized_frame = cv2.resize(frame, (640, 640))  # Resize to model input size
        normalized_frame = resized_frame / 255.0  # Normalize pixel values to [0, 1]
        transposed_frame = np.transpose(normalized_frame, (2, 0, 1))  # HWC to CHW
        input_tensor = np.expand_dims(transposed_frame, axis=0).astype(np.float32)  # Add batch dimension
        return input_tensor

    def postprocess_and_print(self, outputs, frame):
        """Post-process the ONNX model outputs and print detected objects."""
        detections = outputs[0]  # Assuming the first output contains detections
        for detection in detections:
            x1, y1, x2, y2, conf, cls = detection[:6]
            if conf > 0.6:  # Confidence threshold
                class_name = f"Class {int(cls)}"  # Replace with actual class names if available
                print(f"Detected {class_name} with {conf:.2f} confidence at [{x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}]")

# Example usage
if __name__ == "__main__":
    model_path = "yolov5s.onnx"  # Path to the ONNX model
    camera = HeadlessCamera(resolution=(160, 120), frame_rate=30, model_path=model_path)
    camera.start()

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        camera.stop()