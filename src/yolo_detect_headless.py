import cv2
from ultralytics import YOLO
from picamera2 import Picamera2

class YOLODetector:
    def __init__(self, model_path, resolution=(640,360), confidence_threshold=0.6):
        """
        Initialize the YOLODetector class.
        
        Args:
            model_path (str): Path to the YOLO model file.
            resolution (tuple): Resolution of the camera frames (width, height).
            confidence_threshold (float): Minimum confidence for detections to be considered valid.
        """        
        self.model_path = model_path
        self.resolution = resolution
        self.confidence_threshold = confidence_threshold

        # Load the YOLO model for object detection
        self.model = YOLO(self.model_path, task='detect')
        self.labels = self.model.names  # Class labels for detected objects

        # Initialize the Picamera with the specified resolution
        self.picam = Picamera2()
        self.picam.configure(self.picam.create_video_configuration(main={"format": 'XRGB8888', "size": self.resolution}))
        self.picam.start()

    def detect_objects(self):
        """
        Perform real-time object detection using the YOLO model and Picamera.
        """
        try:
            print("Starting real-time object detection...")
            while True:
                # Capture a frame from the Picamera
                frame_bgra = self.picam.capture_array()
                frame = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)

                # Run YOLO inference on the captured frame
                results = self.model(frame, verbose=False)
                detections = results[0].boxes # Extract bounding boxes from results

                # Initialize object count and detected objects list
                object_count = 0
                detected_objects = []                

                # Process each detection
                for i in range(len(detections)):
                    # Get bounding box coordinates
                    xyxy_tensor = detections[i].xyxy.cpu()
                    xyxy = xyxy_tensor.numpy().squeeze()
                    xmin, ymin, xmax, ymax = xyxy.astype(int)

                    # Get class ID, name, and confidence score
                    classidx = int(detections[i].cls.item())
                    classname = self.labels[classidx]
                    conf = detections[i].conf.item()

                    # Filter detections based on confidence threshold
                    if conf > self.confidence_threshold:
                        object_count += 1
                        detected_objects.append({
                            "type": classname,
                            "confidence": conf,
                            "bounding_box": [xmin, ymin, xmax, ymax]
                        })

                # Print detection details only if objects are detected
                # if detected_objects:
                #     self.print_detection_details(detected_objects)
    
        except KeyboardInterrupt:
            print("\nStopping detection...")

        finally:
            self.cleanup()

    def print_detection_details(self, detected_objects):
        """
        Print details of detected objects.
        
        Args:
            detected_objects (list): List of dictionaries containing detection details.
        """
        print("\nDetected objects in the current frame:")
        for idx, obj in enumerate(detected_objects, start=1):
            print(f"Object {idx}:")
            print(f"  Type: {obj['type']}")
            print(f"  Confidence: {obj['confidence']:.2f}")
            print(f"  Bounding Box: {obj['bounding_box']}")
        print(f"Total objects detected: {len(detected_objects)}")

    def cleanup(self):
        """
        Clean up resources such as the Picamera when detection is stopped.
        """
        self.picam.stop()
        print("Detection stopped.")

# Example usage
if __name__ == "__main__":
    """
    Example main function to run the object detection model.
    """
    detector = YOLODetector(model_path="yolov5nu_ncnn_model")
    detector.detect_objects()