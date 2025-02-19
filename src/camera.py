import cv2
import numpy as np
import time

# Function to find a working video source
def find_working_camera():
    for i in range(10):
        camera = cv2.VideoCapture(i)
        if camera.isOpened():
            return camera
        camera.release()
    return None

# Initialize the camera
camera = find_working_camera()
if camera is None:
    print("No working camera found")
    exit()

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 32)

# Allow the camera to warm up
time.sleep(0.1)

while True:
    # Capture a frame
    ret, frame = camera.read()

    # Check if the frame was captured successfully
    if not ret:
        print("Failed to capture frame")
        break

    # Display the frame
    cv2.imshow("Camera Feed", frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
camera.release()
cv2.destroyAllWindows()