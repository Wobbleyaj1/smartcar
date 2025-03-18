from picamera2 import Picamera2
import time

class HeadlessCamera:
    def __init__(self, resolution=(320, 240), frame_rate=30, dataset=None):
        """
        Initialize the HeadlessCamera.

        :param resolution: Tuple specifying the resolution of the camera (width, height).
        :param frame_rate: Integer specifying the frame rate of the camera.
        :param dataset: Optional dataset to use for processing frames.
        """
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": resolution, "format": "RGB888"}))
        self.picam2.set_controls({"FrameRate": frame_rate})
        self.running = False
        self.dataset = dataset  # Store the dataset

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

                # Process the frame using the dataset (if provided)
                if self.dataset:
                    self.process_frame_with_dataset(frame)

                # Add a small delay to simulate processing time
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            self.stop()

    def process_frame_with_dataset(self, frame):
        """
        Process the captured frame using the dataset.

        :param frame: The captured frame as a NumPy array.
        """
        # Example: Print a message indicating the dataset is being used
        print(f"Processing frame with dataset: {self.dataset}")

# Example usage
if __name__ == "__main__":
    # Pass a dataset as a parameter (e.g., a string representing the dataset name)
    dataset = "example_dataset"
    camera = HeadlessCamera(resolution=(320, 240), frame_rate=30, dataset=dataset)
    camera.start()
    camera.capture_frames()