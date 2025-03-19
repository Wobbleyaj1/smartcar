import time
import cv2
import numpy as np
from ultralytics import YOLO
from picamera2 import Picamera2

class YOLODetector:
    def __init__(self, model_path, resolution=(1280, 720), confidence_threshold=0.6):
        self.model_path = model_path
        self.resolution = resolution
        self.confidence_threshold = confidence_threshold

        # Load the YOLO model
        self.model = YOLO(self.model_path, task='detect')
        self.labels = self.model.names  # Class labels

        # Initialize the Picamera
        self.picam = Picamera2()
        self.picam.configure(self.picam.create_video_configuration(main={"format": 'XRGB8888', "size": self.resolution}))
        self.picam.start()

    def detect_objects(self):
        try:
            print("Starting real-time object detection...")
            while True:
                # Capture a frame from the Picamera
                frame_bgra = self.picam.capture_array()
                frame = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)

                # Run inference on the frame
                results = self.model(frame, verbose=False)
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
                    classname = self.labels[classidx]
                    conf = detections[i].conf.item()

                    # Filter detections by confidence threshold
                    if conf > self.confidence_threshold:
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
            self.cleanup()

    def cleanup(self):
        # Clean up resources
        self.picam.stop()
        print("Detection stopped.")

# Example usage
if __name__ == "__main__":
    detector = YOLODetector(model_path="yolov5nu_ncnn_model")
    detector.detect_objects()