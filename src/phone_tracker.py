from pantilt import PanTiltController
from yolo_detect_headless import YOLODetector
import time
import cv2

class PhoneTracker:
    def __init__(self, model_path, object="cell phone", resolution=(640, 360), confidence_threshold=0.6):
        self.pan_tilt = PanTiltController()
        self.detector = YOLODetector(model_path, resolution, confidence_threshold)
        self.phone_label = object
        self.frame_width, self.frame_height = resolution

    def track_phone(self):
        try:
            print("Starting phone tracking...")
            while True:
                # Capture a frame and run object detection
                frame_bgra = self.detector.picam.capture_array()
                frame = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)
                results = self.detector.model(frame, verbose=False)
                detections = results[0].boxes

                # Find the phone in the detections
                phone_bbox = None
                for i in range(len(detections)):
                    classidx = int(detections[i].cls.item())
                    classname = self.detector.labels[classidx]
                    conf = detections[i].conf.item()

                    if classname == self.phone_label and conf > self.detector.confidence_threshold:
                        xyxy_tensor = detections[i].xyxy.cpu()
                        xyxy = xyxy_tensor.numpy().squeeze()
                        phone_bbox = xyxy.astype(int)  # [xmin, ymin, xmax, ymax]
                        break

                if phone_bbox is not None:
                    # Calculate the center of the phone's bounding box
                    xmin, ymin, xmax, ymax = phone_bbox
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

                    # Adjust pan-tilt to center the phone
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

                time.sleep(0.1)  # Add a small delay to avoid overwhelming the system

        except KeyboardInterrupt:
            print("\nStopping phone tracking...")
        finally:
            self.detector.cleanup()

# Example usage
if __name__ == "__main__":
    tracker = PhoneTracker(model_path="yolov5nu_ncnn_model", object="person")
    tracker.track_phone()