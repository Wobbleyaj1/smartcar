import RPi.GPIO as GPIO
from time import sleep

# Stops all warnings from appearing
GPIO.setwarnings(False)

# We name all the pins on BOARD mode
GPIO.setmode(GPIO.BOARD)

# Set up the GPIO pins for the buttons
BUTTON_UP = 11  # BOARD pin 11 corresponds to GPIO 17
BUTTON_DOWN = 13  # BOARD pin 13 corresponds to GPIO 27
GPIO.setup(BUTTON_UP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    print("Starting button test...")
    while True:
        if GPIO.input(BUTTON_UP) == GPIO.HIGH: # Button pressed
            print("Button UP pressed")
        if GPIO.input(BUTTON_DOWN) == GPIO.HIGH: # Button pressed
            print("Button DOWN pressed")
        sleep(0.1) # Small delay to debounce
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup() # Clean up all the ports we've used
    print("Button test stopped and GPIO cleaned up.")