from picamera2 import Picamera2
from ultralytics import YOLO
import time
import cv2
import numpy as np

# Load the pre-trained model
model = YOLO('mouseModel.pt')  # Ensure mouseModel.pt is in the same directory

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (320, 240), "format": "RGB888"}))

# Set the frame rate
picam2.set_controls({"FrameRate": 30})

picam2.start()

# Allow the camera to warm up
time.sleep(0.1)

try:
    while True:
        # Capture a frame
        frame = picam2.capture_array()

        # Convert the frame to RGB (if needed by the model)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run the frame through the model
        results = model.predict(source=rgb_frame, conf=0.6, verbose=False)

        # Parse the results
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                if conf >= 0.6:  # Check confidence threshold
                    print(f"Mouse detected with {conf:.2f} confidence at [{x1:.0f}, {y1:.0f}, {x2:.0f}, {y2:.0f}]")

        # Add a small delay to simulate processing time
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    # Release the camera
    picam2.stop()
    print("Camera stopped")