from picamera2 import Picamera2, Preview
import cv2
import time

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (160, 120), "format": "RGB888"}))

# Set the frame rate
picam2.set_controls({"FrameRate": 30})

picam2.start()

# Allow the camera to warm up
time.sleep(0.1)

while True:
    # Capture a frame
    frame = picam2.capture_array()

    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # Display the grayscale frame
    cv2.imshow("Camera Feed", gray_frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
picam2.stop()
cv2.destroyAllWindows()