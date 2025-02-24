import threading
import pigpio
import RPi.GPIO as GPIO
from time import sleep
from picamera2 import Picamera2, Preview
import cv2
import time

class ServoControl:
    def __init__(self, stop_event):
        self.stop_event = stop_event
        self.pi = pigpio.pi()
        if not self.pi.connected:
            print("Failed to connect to pigpio daemon. Please start it with 'sudo pigpiod'.")
            exit()

        self.SERVO_PIN_1 = 22
        self.SERVO_PIN_2 = 18

        self.duty_cycle_1 = 7.5  # Neutral position (90 degrees)
        self.duty_cycle_2 = 7.5  # Neutral position (90 degrees)

        self.pi.set_PWM_frequency(self.SERVO_PIN_1, 50)
        self.pi.set_PWM_frequency(self.SERVO_PIN_2, 50)

    def oscillate_servos(self):
        direction_1 = 1
        direction_2 = -1
        while not self.stop_event.is_set():
            self.duty_cycle_1 += direction_1 * 0.1
            self.duty_cycle_2 += direction_2 * 0.1

            if self.duty_cycle_1 >= 12.5 or self.duty_cycle_1 <= 2.5:
                direction_1 *= -1
            if self.duty_cycle_2 >= 12.5 or self.duty_cycle_2 <= 2.5:
                direction_2 *= -1

            pulse_width_1 = 500 + (self.duty_cycle_1 - 2.5) * 200
            pulse_width_2 = 500 + (self.duty_cycle_2 - 2.5) * 200

            self.pi.set_servo_pulsewidth(self.SERVO_PIN_1, pulse_width_1)
            self.pi.set_servo_pulsewidth(self.SERVO_PIN_2, pulse_width_2)

            sleep(0.1)

    def cleanup(self):
        self.pi.set_servo_pulsewidth(self.SERVO_PIN_1, 0)
        self.pi.set_servo_pulsewidth(self.SERVO_PIN_2, 0)
        GPIO.cleanup()
        print("Servo control loop stopped and pigpio cleaned up.")

def main():
    stop_event = threading.Event()
    servo_control = ServoControl(stop_event)

    # Initialize the camera
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
    picam2.start()

    # Allow the camera to warm up
    time.sleep(0.1)

    try:
        # Start the servo oscillation in a separate thread
        servo_thread = threading.Thread(target=servo_control.oscillate_servos)
        servo_thread.start()

        while True:
            # Capture a frame
            frame = picam2.capture_array()

            # Display the frame
            cv2.imshow("Camera Feed", frame)

            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        stop_event.set()

    finally:
        stop_event.set()
        servo_thread.join()
        servo_control.cleanup()
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()