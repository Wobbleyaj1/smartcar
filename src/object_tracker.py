from pantilt import PanTiltController
from yolo_detect_headless import YOLODetector
import time
import cv2

class ObjectTracker:
    def __init__(self, model_path, object="person", resolution=(640, 360), confidence_threshold=0.6):
        self.pan_tilt = PanTiltController()
        self.detector = YOLODetector(model_path, resolution, confidence_threshold)
        self.object_class = object
        self.frame_width, self.frame_height = resolution

    def track_object(self):
        try:
            # Initialize the pan-tilt mechanism
            self.pan_tilt.initialize_to_middle()

            # Start the camera
            print("Starting object tracking...")
            detection_count = 0
            start_time = time.time()  # Start the timer

            while True:
                # Capture a frame and run object detection
                frame_bgra = self.detector.picam.capture_array()
                frame = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)
                results = self.detector.model(frame, verbose=False)
                detections = results[0].boxes

                # Find the object in the detections
                object_bbox = None
                for i in range(len(detections)):
                    classidx = int(detections[i].cls.item())
                    classname = self.detector.labels[classidx]
                    conf = detections[i].conf.item()

                    if classname == self.object_class and conf > self.detector.confidence_threshold:
                        xyxy_tensor = detections[i].xyxy.cpu()
                        xyxy = xyxy_tensor.numpy().squeeze()
                        object_bbox = xyxy.astype(int)  # [xmin, ymin, xmax, ymax]
                        detection_count += 1  # Increment detection count
                        break

                if object_bbox is not None:
                    # Calculate the center of the object's bounding box
                    xmin, ymin, xmax, ymax = object_bbox
                    bbox_center_x = (xmin + xmax) // 2
                    bbox_center_y = (ymin + ymax) // 2

                    # Calculate offsets from the frame center
                    frame_center_x = self.frame_width // 2
                    frame_center_y = self.frame_height // 2
                    offset_x = bbox_center_x - frame_center_x
                    offset_y = bbox_center_y - frame_center_y

                    # Dynamically adjust step size based on the offset
                    step_x = min(abs(offset_x) // 10, 10)  # Scale step size, max 10
                    step_y = min(abs(offset_y) // 10, 10)  # Scale step size, max 10

                    # Adjust pan-tilt to center the object
                    if abs(offset_x) > 10:  # Threshold to avoid jitter
                        if offset_x > 0:
                            # Move right to align the bounding box center
                            self.pan_tilt.servo_degree_decrease(self.pan_tilt.SERVO_DOWN_CH, step_x)
                        else:
                            # Move left to align the bounding box center
                            self.pan_tilt.servo_degree_increase(self.pan_tilt.SERVO_DOWN_CH, step_x)

                    if abs(offset_y) > 20:  # Threshold to avoid jitter
                        if offset_y > 0:
                            # Move down to align the bounding box center
                            self.pan_tilt.servo_degree_increase(self.pan_tilt.SERVO_UP_CH, step_y)
                        else:
                            # Move up to align the bounding box center
                            self.pan_tilt.servo_degree_decrease(self.pan_tilt.SERVO_UP_CH, step_y)

                # Log detections per second
                elapsed_time = time.time() - start_time
                if elapsed_time >= 1.0:  # Log every second
                    print(f"Detections per second: {detection_count}")
                    detection_count = 0  # Reset the count
                    start_time = time.time()  # Reset the timer

                time.sleep(0.0001)  # Add a small delay for smoother updates

        except KeyboardInterrupt:
            print("\nStopping object tracking...")
        finally:
            self.detector.cleanup()

# Example usage
if __name__ == "__main__":
    tracker = ObjectTracker(model_path="yolov5nu_ncnn_model", object="person")
    tracker.track_object()