import cv2
import numpy as np
import time

# Initialize the camera
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 32)

# Allow the camera to warm up
time.sleep(0.1)

# Capture an image
ret, image = camera.read()

# Check if the image was captured successfully
if not ret:
    print("Failed to capture image")
    camera.release()
    cv2.destroyAllWindows()
    exit()

# Display the image
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Release the camera
camera.release()