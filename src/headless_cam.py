from picamera2 import Picamera2
import time

class HeadlessCamera:
    def __init__(self, resolution=(320, 240), frame_rate=30):
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": resolution, "format": "RGB888"}))
        self.picam2.set_controls({"FrameRate": frame_rate})
        self.running = False

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

                # Process the frame (e.g., save it, analyze it, etc.)
                print("Frame captured")

                # Add a small delay to simulate processing time
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            self.stop()

# Example usage
if __name__ == "__main__":
    camera = HeadlessCamera(resolution=(320, 240), frame_rate=30)
    camera.start()
    camera.capture_frames()