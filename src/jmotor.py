import RPi.GPIO as io
import time

io.setmode(io.BCM)

# Update GPIO pin numbers to match physical pins 16 and 18
in1_pin = 23  # GPIO 23 corresponds to physical pin 16
in2_pin = 24  # GPIO 24 corresponds to physical pin 18

io.setup(in1_pin, io.OUT)
io.setup(in2_pin, io.OUT)

# Set up software PWM on in1_pin
pwm = io.PWM(in1_pin, 500)  # 500Hz frequency
pwm.start(0)  # Start with 0% duty cycle

def set_duty_cycle(duty):
    """Set the PWM duty cycle."""
    print(f"Setting duty cycle to: {duty}%")
    pwm.ChangeDutyCycle(duty)

def clockwise():
    """Set motor to spin clockwise."""
    io.output(in1_pin, True)
    io.output(in2_pin, False)

def counter_clockwise():
    """Set motor to spin counter-clockwise."""
    io.output(in1_pin, False)
    io.output(in2_pin, True)

# Start motor in clockwise direction
clockwise()

while True:
    try:
        cmd = input("Command, f/r 0..9, E.g. f5 :")  # Get user input
        if len(cmd) < 2:
            print("Invalid command. Use format f5 or r3.")
            continue

        direction = cmd[0]
        if direction == "f":
            print("Setting motor to clockwise")
            clockwise()
        elif direction == "r":
            print("Setting motor to counter-clockwise")
            counter_clockwise()
        else:
            print("Invalid direction. Use 'f' for forward or 'r' for reverse.")
            continue

        # Set speed based on the second character of the command
        speed = int(cmd[1]) * 11  # Convert 0-9 to 0%-99% duty cycle
        set_duty_cycle(speed)

    except ValueError:
        print("Invalid speed. Use a number between 0 and 9.")
    except KeyboardInterrupt:
        print("\nExiting program.")
        break

# Cleanup GPIO and stop PWM
pwm.stop()
io.cleanup()