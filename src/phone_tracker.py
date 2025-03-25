from pantilt import PanTiltController
from yolo_detect_headless import YOLODetector
import time
import cv2

class MouseTracker:
    def __init__(self, model_path, resolution=(1280, 720), confidence_threshold=0.6):
        self.detector = YOLODetector(model_path, resolution, confidence_threshold)
        self.controller = PanTiltController()
        self.frame_center = (resolution[0] // 2, resolution[1] // 2)
        self.tolerance = 20  # Pixels tolerance for centering

        # Initialize the pan-tilt mechanism to the middle position
        print("Initializing PanTiltController to the middle position...")
        self.controller.initialize_to_middle()

    def track_mouse(self):
        print("Starting mouse tracking...")
        try:
            while True:
                # Capture detections from YOLO
                frame_bgra = self.detector.picam.capture_array()
                frame = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)
                results = self.detector.model(frame, verbose=False)
                detections = results[0].boxes

                # Process detections to find a cell phone
                for i in range(len(detections)):
                    classidx = int(detections[i].cls.item())
                    classname = self.detector.labels[classidx]
                    conf = detections[i].conf.item()

                    if classname == "cell phone" and conf > self.detector.confidence_threshold:
                        # Get bounding box
                        xyxy_tensor = detections[i].xyxy.cpu()
                        xyxy = xyxy_tensor.numpy().squeeze()
                        xmin, ymin, xmax, ymax = xyxy.astype(int)

                        # Calculate the center of the bounding box
                        obj_center = ((xmin + xmax) // 2, (ymin + ymax) // 2)

                        # Adjust the camera to center the object
                        self.adjust_camera(obj_center)
                        break  # Focus on the first detected object

                # Reduce the delay to increase detection frequency
                time.sleep(0.05)  # Reduced from 0.1 to 0.05 seconds

        except KeyboardInterrupt:
            print("\nStopping mouse tracking...")

        finally:
            self.detector.cleanup()

    def adjust_camera(self, obj_center):
        x_diff = obj_center[0] - self.frame_center[0]
        y_diff = obj_center[1] - self.frame_center[1]

        # Adjust horizontal (pan)
        if abs(x_diff) > self.tolerance:
            if x_diff > 0:
                new_degree = min(self.controller.servo_down_degree + abs(x_diff) // self.controller.STEP, self.controller.SERVO_DOWN_MAX)
                self.controller.set_servo_degree(self.controller.SERVO_DOWN_CH, new_degree)
            else:
                new_degree = max(self.controller.servo_down_degree - abs(x_diff) // self.controller.STEP, self.controller.SERVO_DOWN_MIN)
                self.controller.set_servo_degree(self.controller.SERVO_DOWN_CH, new_degree)
            time.sleep(0.02)  # Add a small delay after pan adjustment

        # Adjust vertical (tilt)
        if abs(y_diff) > self.tolerance:
            if y_diff > 0:
                new_degree = min(self.controller.servo_up_degree + abs(y_diff) // self.controller.STEP, self.controller.SERVO_UP_MAX)
                self.controller.set_servo_degree(self.controller.SERVO_UP_CH, new_degree)
            else:
                new_degree = max(self.controller.servo_up_degree - abs(y_diff) // self.controller.STEP, self.controller.SERVO_UP_MIN)
                self.controller.set_servo_degree(self.controller.SERVO_UP_CH, new_degree)
            time.sleep(0.02)  # Add a small delay after tilt adjustment


if __name__ == "__main__":
    tracker = MouseTracker(model_path="yolov5nu_ncnn_model")
    tracker.track_mouse()