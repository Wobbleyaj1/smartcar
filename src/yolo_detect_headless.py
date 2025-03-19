import time
import cv2
import numpy as np
from ultralytics import YOLO
from picamera2 import Picamera2

# Configuration
MODEL_PATH = "yolov5nu_ncnn_model"  # Replace with the path to your YOLO model
RESOLUTION = (1280, 720)  # Resolution for the Picamera
CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence threshold for detections

# Load the YOLO model
model = YOLO(MODEL_PATH, task='detect')
labels = model.names  # Class labels

# Initialize the Picamera
picam = Picamera2()
picam.configure(picam.create_video_configuration(main={"format": 'XRGB8888', "size": RESOLUTION}))
picam.start()

try:
    print("Starting real-time object detection...")
    while True:
        # Capture a frame from the Picamera
        frame_bgra = picam.capture_array()
        frame = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)

        # Run inference on the frame
        results = model(frame, verbose=False)
        detections = results[0].boxes

        # Initialize object count
        object_count = 0

        # Process detections
        print("\nDetected objects in the current frame:")
        for i in range(len(detections)):
            # Get bounding box coordinates
            xyxy_tensor = detections[i].xyxy.cpu()
            xyxy = xyxy_tensor.numpy().squeeze()
            xmin, ymin, xmax, ymax = xyxy.astype(int)

            # Get class ID, name, and confidence
            classidx = int(detections[i].cls.item())
            classname = labels[classidx]
            conf = detections[i].conf.item()

            # Filter detections by confidence threshold
            if conf > CONFIDENCE_THRESHOLD:
                object_count += 1
                print(f"Object {object_count}:")
                print(f"  Type: {classname}")
                print(f"  Confidence: {conf:.2f}")
                print(f"  Bounding Box: [xmin: {xmin}, ymin: {ymin}, xmax: {xmax}, ymax: {ymax}]")

        # Print total number of objects detected
        print(f"Total objects detected: {object_count}")

        # Add a small delay to avoid overwhelming the terminal
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nStopping detection...")

finally:
    # Clean up resources
    picam.stop()
    print("Detection stopped.")