import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

TRIG = 23
ECHO = 24

print("Distance measurement in progress")

GPIO.setup(TRIG, GPIO.OUT)  
GPIO.setup(ECHO, GPIO.IN)

previous_distance = None

try:
    while True:
        GPIO.output(TRIG, False)
        time.sleep(.5)

        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        timeout = time.time() + 1  # 1 second timeout
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
            if time.time() > timeout:
                pulse_start = None
                break

        if pulse_start is None:
            continue

        timeout = time.time() + 1  # 1 second timeout
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
            if time.time() > timeout:
                pulse_end = None
                break

        if pulse_end is None:
            continue

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        if previous_distance is None or abs(distance - previous_distance) >= 10:
            print("Distance:", distance, "cm")
            previous_distance = distance

except KeyboardInterrupt:
    print("Measurement stopped by user")
    GPIO.cleanup()