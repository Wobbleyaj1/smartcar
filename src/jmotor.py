import RPi.GPIO as io
import time

io.setmode(io.BCM)

# Update GPIO pin numbers to match physical pins 16 and 18
in1_pin = 23  # GPIO 23 corresponds to physical pin 16
in2_pin = 24  # GPIO 24 corresponds to physical pin 18

io.setup(in1_pin, io.OUT)
io.setup(in2_pin, io.OUT)

# Set up software PWM on both pins
pwm_in1 = io.PWM(in1_pin, 500)  # 500Hz frequency
pwm_in2 = io.PWM(in2_pin, 500)  # 500Hz frequency
pwm_in1.start(0)  # Start with 0% duty cycle
pwm_in2.start(0)  # Start with 0% duty cycle

def set_motor_speed(direction, duty):
    """Set the motor speed and direction."""
    print(f"Setting motor to {'clockwise' if direction == 'f' else 'counter-clockwise'} at {duty}% duty cycle")
    if direction == "f":
        pwm_in1.ChangeDutyCycle(duty)
        pwm_in2.ChangeDutyCycle(0)
    elif direction == "r":
        pwm_in1.ChangeDutyCycle(0)
        pwm_in2.ChangeDutyCycle(duty)

while True:
    try:
        cmd = input("Command, f/r 0..9, E.g. f5 :")  # Get user input
        if len(cmd) < 2:
            print("Invalid command. Use format f5 or r3.")
            continue

        direction = cmd[0]
        if direction not in ["f", "r"]:
            print("Invalid direction. Use 'f' for forward or 'r' for reverse.")
            continue

        # Set speed based on the second character of the command
        speed = int(cmd[1]) * 11  # Convert 0-9 to 0%-99% duty cycle
        set_motor_speed(direction, speed)

    except ValueError:
        print("Invalid speed. Use a number between 0 and 9.")
    except KeyboardInterrupt:
        print("\nExiting program.")
        break

# Cleanup GPIO and stop PWM
pwm_in1.stop()
pwm_in2.stop()
io.cleanup()