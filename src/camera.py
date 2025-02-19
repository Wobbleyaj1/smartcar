import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import time

# Initialize the camera
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# Allow the camera to warm up
time.sleep(0.1)

# Capture an image
camera.capture(rawCapture, format="bgr")
image = rawCapture.array

# Display the image
cv2.imshow("Image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()