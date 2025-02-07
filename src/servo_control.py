import pigpio
import RPi.GPIO as GPIO
from time import sleep

# Initialize pigpio
pi = pigpio.pi()

# Define GPIO pin for PWM
SERVO_PIN_1 = 22
SERVO_PIN_2 = 18

# Set initial duty cycle
duty_cycle_1 = 7.5  # Neutral position (90 degrees)
duty_cycle_2 = 7.5  # Neutral position (90 degrees)

# Set PWM frequency to 50Hz (standard for servos)
pi.set_PWM_frequency(SERVO_PIN_1, 50)

# Setup GPIO for button inputs
BUTTON_UP_1 = 17
BUTTON_DOWN_1 = 27
BUTTON_UP_2 = 5
BUTTON_DOWN_2 = 6
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_UP_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_DOWN_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_UP_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_DOWN_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    print("Starting servo control loop...")
    while True:
        button_up_state_1 = GPIO.input(BUTTON_UP_1)
        button_down_state_1 = GPIO.input(BUTTON_DOWN_1)
        button_up_state_2 = GPIO.input(BUTTON_UP_2)
        button_down_state_2 = GPIO.input(BUTTON_DOWN_2)
        print(f"Button UP state: {button_up_state_1}, Button DOWN state: {button_down_state_1}")

        # Control servo 1
        if button_up_state_1 == GPIO.HIGH:  # Button pressed
            duty_cycle_1 += 0.1  # Increase duty cycle to turn right
            if duty_cycle_1 > 12.5:  # Limit to +90 deg position
                duty_cycle_1 = 12.5
            pulse_width_1 = 500 + (duty_cycle_1 - 2.5) * 200  # Convert duty cycle to pulse width
            pi.set_servo_pulsewidth(SERVO_PIN_1, pulse_width_1)
            print(f"Button UP pressed. Duty cycle increased to {duty_cycle_1}, pulse width set to {pulse_width_1}")
        elif button_down_state_1 == GPIO.HIGH:  # Button pressed
            duty_cycle_1 -= 0.1  # Decrease duty cycle to turn left
            if duty_cycle_1 < 6:  # Limit to -90 deg position
                duty_cycle_1 = 6
            pulse_width_1 = 500 + (duty_cycle_1 - 2.5) * 200  # Convert duty cycle to pulse width
            pi.set_servo_pulsewidth(SERVO_PIN_1, pulse_width_1)
            print(f"Button DOWN pressed. Duty cycle decreased to {duty_cycle_1}, pulse width set to {pulse_width_1}")

        # Control servo 2
        if button_up_state_2 == GPIO.HIGH:  # Button pressed
            duty_cycle_2 += 0.1  # Increase duty cycle to turn right
            if duty_cycle_2 > 12.5:  # Limit to +90 deg position
                duty_cycle_2 = 12.5
            pulse_width_2 = 500 + (duty_cycle_2 - 2.5) * 200  # Convert duty cycle to pulse width
            pi.set_servo_pulsewidth(SERVO_PIN_2, pulse_width_2)
            print(f"Button UP pressed. Duty cycle increased to {duty_cycle_2}, pulse width set to {pulse_width_2}")
        elif button_down_state_2 == GPIO.HIGH:  # Button pressed
            duty_cycle_2 -= 0.1  # Decrease duty cycle to turn left
            if duty_cycle_2 < 6:  # Limit to -90 deg position
                duty_cycle_2 = 6
            pulse_width_2 = 500 + (duty_cycle_2 - 2.5) * 200  # Convert duty cycle to pulse width
            pi.set_servo_pulsewidth(SERVO_PIN_2, pulse_width_2)
            print(f"Button DOWN pressed. Duty cycle decreased to {duty_cycle_2}, pulse width set to {pulse_width_2}")
        sleep(0.01)  # Small delay to debounce
except KeyboardInterrupt:
    pass
finally:
    pi.set_servo_pulsewidth(SERVO_PIN_1, 0)  # Stop servo 1
    pi.set_servo_pulsewidth(SERVO_PIN_2, 0)  # Stop servo 2
    GPIO.cleanup()  # Clean up GPIO
    print("Servo control loop stopped and pigpio cleaned up.")