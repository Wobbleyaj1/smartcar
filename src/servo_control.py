import RPi.GPIO as GPIO
from gpiozero import Button
from time import sleep

# Stops all warnings from appearing
GPIO.setwarnings(False)

# We name all the pins on BOARD mode
GPIO.setmode(GPIO.BOARD)

# Set an output for the PWM Signal
GPIO.setup(16, GPIO.OUT)

# Set up the PWM on pin #16 at 50Hz
pwm = GPIO.PWM(16, 50)
pwm.start(7.5) # Start the servo at neutral position (0 deg position)

# Set up the GPIO pins for the buttons
BUTTON_UP = Button(2)
BUTTON_DOWN = Button(3)

try:
    duty_cycle = 7.5 # Neutral position
    while True:
        if GPIO.input(BUTTON_UP) == GPIO.LOW: # Button pressed
            duty_cycle += 0.1 # Increase duty cycle to turn right
            if duty_cycle > 12.5: # Limit to +90 deg position
                duty_cycle = 12.5
            pwm.ChangeDutyCycle(duty_cycle)
        elif GPIO.input(BUTTON_DOWN) == GPIO.LOW: # Button pressed
            duty_cycle -= 0.1 # Decrease duty cycle to turn left
            if duty_cycle < 2.5: # Limit to -90 deg position
                duty_cycle = 2.5
            pwm.ChangeDutyCycle(duty_cycle)
        sleep(0.1) # Small delay to control the speed of turning
except KeyboardInterrupt:
    pass
finally:
    pwm.stop() # Stop the servo
    GPIO.cleanup() # Clean up all the ports we've used