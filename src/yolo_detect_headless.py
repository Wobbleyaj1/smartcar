import time
import cv2
import numpy as np
from ultralytics import YOLO
from picamera2 import Picamera2

class YOLODetector:
    def __init__(self, model_path, resolution=(640,360), confidence_threshold=0.6):
        self.model_path = model_path
        self.resolution = resolution
        self.confidence_threshold = confidence_threshold

        # Load the YOLO model
        self.model = YOLO(self.model_path, task='detect')
        self.labels = self.model.names  # Class labels

        # Initialize the Picamera
        self.picam = Picamera2()
        self.picam.configure(self.picam.create_video_configuration(main={"format": 'XRGB8888', "size": self.resolution, "fps": 30}))
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
                detected_objects = []
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
                        detected_objects.append({
                            "type": classname,
                            "confidence": conf,
                            "bounding_box": [xmin, ymin, xmax, ymax]
                        })

                # Print detection details only if objects are detected
                if object_count > 0:
                    print("\nDetected objects in the current frame:")
                    for idx, obj in enumerate(detected_objects, start=1):
                        print(f"Object {idx}:")
                        print(f"  Type: {obj['type']}")
                        print(f"  Confidence: {obj['confidence']:.2f}")
                        print(f"  Bounding Box: {obj['bounding_box']}")
                    print(f"Total objects detected: {object_count}")

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