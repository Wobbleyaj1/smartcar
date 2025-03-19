import RPi.GPIO as GPIO
from time import sleep

# Motor class using RPI.GPIO
# Benefits of RPi.GPIO:
# - Lower-level control, including PWM frequency setting.
# - Great if you need to tune PWM frequencies for smoother motor operation.
# - More flexible but more code.

class Motor:
    def __init__(self, in1, in2, enable):
        self.in1 = in1
        self.in2 = in2
        self.enable = enable
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.enable, GPIO.OUT)
        self.pwm = GPIO.PWM(self.enable, 1000)  # 1kHz frequency
        self.pwm.start(0)
    
    def forward(self, speed):
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.LOW)
        self.pwm.ChangeDutyCycle(speed)  # 0-100%
    
    def backward(self, speed):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(speed)   # 0-100%
    
    def stop(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        self.pwm.ChangeDutyCycle(0)


'''
# Example motor definitions (adjust GPIO pins later)
GPIO.setmode(GPIO.BCM)
motor1 = Motor(17, 18, 13)
motor2 = Motor(22, 23, 12)

# Example test
motor1.forward(50)   # 50% speed
sleep(2)
motor1.backward(80)  # 80% reverse speed
sleep(2)
motor1.stop()
GPIO.cleanup()
'''