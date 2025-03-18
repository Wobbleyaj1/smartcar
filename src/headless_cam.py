from picamera2 import Picamera2
import torch
import time
import cv2
import numpy as np

# Load the pre-trained model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='mouseModel.pt')  # Ensure mouseModel.pt is in the same directory
model.conf = 0.6  # Set confidence threshold to 60%

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
        results = model(rgb_frame)

        # Parse the results
        for detection in results.xyxy[0]:  # Iterate through detections
            x1, y1, x2, y2, conf, cls = detection.tolist()
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