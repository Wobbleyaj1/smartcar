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

                # Process detections to find a mouse
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

                        # Adjust the camera to center the mouse
                        self.adjust_camera(obj_center)
                        break  # Focus on the first detected mouse

                time.sleep(0.1)  # Small delay to avoid overwhelming the system

        except KeyboardInterrupt:
            print("\nStopping mouse tracking...")

        finally:
            self.detector.cleanup()

    def adjust_camera(self, obj_center):
        x_diff = obj_center[0] - self.frame_center[0]
        y_diff = obj_center[1] - self.frame_center[1]

        # Adjust horizontal (pan)
        if abs(x_diff) > self.tolerance:
            steps = abs(x_diff) // self.controller.STEP  # Calculate number of steps
            if x_diff > 0:
                for _ in range(steps):
                    self.controller.servo_degree_increase(self.controller.SERVO_DOWN_CH, self.controller.STEP)
            else:
                for _ in range(steps):
                    self.controller.servo_degree_decrease(self.controller.SERVO_DOWN_CH, self.controller.STEP)

        # Adjust vertical (tilt)
        if abs(y_diff) > self.tolerance:
            steps = abs(y_diff) // self.controller.STEP  # Calculate number of steps
            if y_diff > 0:
                for _ in range(steps):
                    self.controller.servo_degree_increase(self.controller.SERVO_UP_CH, self.controller.STEP)
            else:
                for _ in range(steps):
                    self.controller.servo_degree_decrease(self.controller.SERVO_UP_CH, self.controller.STEP)


if __name__ == "__main__":
    tracker = MouseTracker(model_path="yolov5nu_ncnn_model")
    tracker.track_mouse()