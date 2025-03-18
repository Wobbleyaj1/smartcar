from picamera2 import Picamera2
import time

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (320, 240), "format": "RGB888"}))

# Set the frame rate
picam2.set_controls({"FrameRate": 30})

picam2.start()

# Allow the camera to warm up
time.sleep(0.001)

try:
    while True:
        # Capture a frame
        frame = picam2.capture_array()

        # Process the frame (e.g., save it, analyze it, etc.)
        # For now, we'll just print a message to indicate a frame was captured
        print("Frame captured")

        # Add a small delay to simulate processing time
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    # Release the camera
    picam2.stop()
    print("Camera stopped")