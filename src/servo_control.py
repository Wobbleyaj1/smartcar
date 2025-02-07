import RPi.GPIO as GPIO
from time import sleep

# Stops all warnings from appearing
GPIO.setwarnings(False)

# We name all the pins on BOARD mode
GPIO.setmode(GPIO.BOARD)

# Set an output for the PWM Signal
GPIO.setup(15, GPIO.OUT)

# Set up the PWM on pin #16 at 50Hz
pwm = GPIO.PWM(15, 50)
pwm.start(7.5) # Start the servo at neutral position (0 deg position)

# Set up the GPIO pins for the buttons
BUTTON_UP = 11  # BOARD pin 11 corresponds to GPIO 17
BUTTON_DOWN = 13  # BOARD pin 13 corresponds to GPIO 27
GPIO.setup(BUTTON_UP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    duty_cycle = 7.5 # Neutral position
    print("Starting servo control loop...")
    while True:
        button_up_state = GPIO.input(BUTTON_UP)
        button_down_state = GPIO.input(BUTTON_DOWN)
        print(f"Button UP state: {button_up_state}, Button DOWN state: {button_down_state}")

        if button_up_state == GPIO.HIGH: # Button pressed
            duty_cycle += 0.1 # Increase duty cycle to turn right
            if duty_cycle > 12.5: # Limit to +90 deg position
                duty_cycle = 12.5
            pwm.ChangeDutyCycle(duty_cycle)
            print(f"Button UP pressed. Duty cycle increased to {duty_cycle}")
        elif button_down_state == GPIO.HIGH: # Button pressed
            duty_cycle -= 0.1 # Decrease duty cycle to turn left
            if duty_cycle < 2.5: # Limit to -90 deg position
                duty_cycle = 2.5
            pwm.ChangeDutyCycle(duty_cycle)
            print(f"Button DOWN pressed. Duty cycle decreased to {duty_cycle}")
        sleep(0.1) # Small delay to debounce
except KeyboardInterrupt:
    pass
finally:
    pwm.stop() # Stop the servo
    GPIO.cleanup() # Clean up all the ports we've used
    print("Servo control loop stopped and GPIO cleaned up.")