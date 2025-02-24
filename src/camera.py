from picamera2 import Picamera2, Preview
import cv2
import time
import torch
import torchvision
from servo_control import ServoControl
import threading

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()

# Load the object detection model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='mouseModel.pt')

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
    results = model(frame)

    # Extract bounding box coordinates
    for det in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = det
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