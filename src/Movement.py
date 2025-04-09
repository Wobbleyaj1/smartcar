import RPI.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

Motor1A = 24
Motor1B = 23
Motor1E = 25

GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor1B, GPIO.OUT)
GPIO.setup(Motor1E, GPIO.OUT)
print("Motor 1 setup complete")

for i in range(3):
    print("Cycle #: " + str(i))

    #Going forward
    GPIO.output(Motor1A, GPIO.HIGH)
    GPIO.output(Motor1B, GPIO.LOW)
    GPIO.output(Motor1E, GPIO.HIGH)
    print("Motor 1 Forward")
    sleep(1)

    #Going backward
    GPIO.output(Motor1A, GPIO.LOW)
    GPIO.output(Motor1B, GPIO.HIGH)
    GPIO.output(Motor1E, GPIO.HIGH)
    print("Motor 1 Backward")
    sleep(1)

#Ending the program
GPIO.output(Motor1E, GPIO.LOW)

GPIO.cleanup()