import pigpio
import RPi.GPIO as GPIO
from time import sleep

# Initialize pigpio
pi = pigpio.pi()

# Define GPIO pin for PWM
SERVO_PIN = 22

# Set initial duty cycle
duty_cycle = 7.5  # Neutral position (90 degrees)

# Set PWM frequency to 50Hz (standard for servos)
pi.set_PWM_frequency(SERVO_PIN, 50)

# Setup GPIO for button inputs
BUTTON_UP = 17
BUTTON_DOWN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_UP, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    print("Starting servo control loop...")
    while True:
        button_up_state = GPIO.input(BUTTON_UP)
        button_down_state = GPIO.input(BUTTON_DOWN)
        print(f"Button UP state: {button_up_state}, Button DOWN state: {button_down_state}")

        if button_up_state == GPIO.HIGH:  # Button pressed
            duty_cycle += 0.1  # Increase duty cycle to turn right
            if duty_cycle > 12.5:  # Limit to +90 deg position
                duty_cycle = 12.5
            pulse_width = 500 + (duty_cycle - 2.5) * 200  # Convert duty cycle to pulse width
            pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)
            print(f"Button UP pressed. Duty cycle increased to {duty_cycle}, pulse width set to {pulse_width}")
        elif button_down_state == GPIO.HIGH:  # Button pressed
            duty_cycle -= 0.1  # Decrease duty cycle to turn left
            if duty_cycle < 2.5:  # Limit to -90 deg position
                duty_cycle = 2.5
            pulse_width = 500 + (duty_cycle - 2.5) * 200  # Convert duty cycle to pulse width
            pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)
            print(f"Button DOWN pressed. Duty cycle decreased to {duty_cycle}, pulse width set to {pulse_width}")
        sleep(0.1)  # Small delay to debounce
except KeyboardInterrupt:
    pass
finally:
    pi.set_servo_pulsewidth(SERVO_PIN, 0)  # Stop the servo
    pi.stop()  # Clean up pigpio
    GPIO.cleanup()  # Clean up GPIO
    print("Servo control loop stopped and pigpio cleaned up.")