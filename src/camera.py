from picamera2 import Picamera2, Preview
import cv2
import time
import torch
import threading
from servo_control import ServoControl
import sys
sys.path.insert(0, 'yolov5')  # Add yolov5 directory to the system path
from models.common import DetectMultiBackend
from utils.general import non_max_suppression, scale_coords
from utils.torch_utils import select_device

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()

# Load the object detection model
device = select_device('')
model = DetectMultiBackend('yolov5/mouseModel.pt', device=device)

# Initialize servo control
stop_event = threading.Event()
servo_control = ServoControl(stop_event)
servo_thread = threading.Thread(target=servo_control.run)
servo_thread.start()

# Allow the camera to warm up
time.sleep(0.1)

while True:
    # Capture a frame
    frame = picam2.capture_array()

    # Perform object detection
    img = torch.from_numpy(frame).to(device)
    img = img.float() / 255.0  # Normalize to [0, 1]
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    pred = model(img)
    pred = non_max_suppression(pred, 0.25, 0.45, classes=None, agnostic=False)

    # Extract bounding box coordinates
    for det in pred[0]:
        if len(det):
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], frame.shape).round()
            for *xyxy, conf, cls in det:
                x1, y1, x2, y2 = xyxy
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                # Draw bounding box and center point
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.circle(frame, (int(center_x), int(center_y)), 5, (0, 0, 255), -1)

                # Control servos based on object position
                frame_center_x = frame.shape[1] / 2
                frame_center_y = frame.shape[0] / 2

                if center_x < frame_center_x - 50:
                    servo_control.duty_cycle_1 += 0.1  # Turn left
                elif center_x > frame_center_x + 50:
                    servo_control.duty_cycle_1 -= 0.1  # Turn right

                if center_y < frame_center_y - 50:
                    servo_control.duty_cycle_2 += 0.1  # Turn up
                elif center_y > frame_center_y + 50:
                    servo_control.duty_cycle_2 -= 0.1  # Turn down

    # Display the frame
    cv2.imshow("Camera Feed", frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
picam2.stop()
cv2.destroyAllWindows()
stop_event.set()
servo_thread.join()