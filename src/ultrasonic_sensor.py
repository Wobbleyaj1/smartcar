import time
import RPi.GPIO as GPIO

class UltrasonicSensor:
    def __init__(self, stop_event):
        self.stop_event = stop_event
        self.TRIG = 23
        self.ECHO = 24
        self.previous_distance = None

    def run(self):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.TRIG, GPIO.OUT)
            GPIO.setup(self.ECHO, GPIO.IN)
            print("Distance measurement in progress")
            while not self.stop_event.is_set():
                GPIO.output(self.TRIG, False)
                time.sleep(0.5)

                GPIO.output(self.TRIG, True)
                time.sleep(0.00001)
                GPIO.output(self.TRIG, False)

                timeout = time.time() + 1  # 1 second timeout
                while GPIO.input(self.ECHO) == 0:
                    pulse_start = time.time()
                    if time.time() > timeout:
                        pulse_start = None
                        break

                if pulse_start is None:
                    continue

                timeout = time.time() + 1  # 1 second timeout
                while GPIO.input(self.ECHO) == 1:
                    pulse_end = time.time()
                    if time.time() > timeout:
                        pulse_end = None
                        break

                if pulse_end is None:
                    continue

                pulse_duration = pulse_end - pulse_start
                distance = pulse_duration * 17150
                distance = round(distance, 2)

                if self.previous_distance is None or abs(distance - self.previous_distance) >= 10:
                    print("Distance:", distance, "cm")
                    self.previous_distance = distance

        finally:
            GPIO.cleanup()
            print("Ultrasonic sensor loop stopped and GPIO cleaned up.")