import RPi.GPIO as io

class MotorController:
    def __init__(self, in1_pin, in2_pin, frequency=500):
        """Initialize the motor controller."""
        self.in1_pin = in1_pin
        self.in2_pin = in2_pin
        self.frequency = frequency

        # Set up GPIO
        io.setmode(io.BCM)
        io.setup(self.in1_pin, io.OUT)
        io.setup(self.in2_pin, io.OUT)

        # Set up PWM
        self.pwm_in1 = io.PWM(self.in1_pin, self.frequency)
        self.pwm_in2 = io.PWM(self.in2_pin, self.frequency)
        self.pwm_in1.start(0)  # Start with 0% duty cycle
        self.pwm_in2.start(0)  # Start with 0% duty cycle

    def set_motor_speed(self, direction, duty):
        """Set the motor speed and direction."""
        #print(f"Setting motor to {'clockwise' if direction == 'f' else 'counter-clockwise'} at {duty}% duty cycle")
        if direction == "f":
            self.pwm_in1.ChangeDutyCycle(duty)
            self.pwm_in2.ChangeDutyCycle(0)
        elif direction == "r":
            self.pwm_in1.ChangeDutyCycle(0)
            self.pwm_in2.ChangeDutyCycle(duty)

    def stop_motor(self):
        """Stop the motor by setting both PWM duty cycles to 0."""
        #print("Stopping the motor.")
        self.pwm_in1.ChangeDutyCycle(0)
        self.pwm_in2.ChangeDutyCycle(0)

    def cleanup(self):
        """Stop PWM and clean up GPIO."""
        #print("Cleaning up GPIO and stopping PWM.")
        self.pwm_in1.stop()
        self.pwm_in2.stop()
        del self.pwm_in1
        del self.pwm_in2
        io.cleanup()

    def stop_pwm(self):
        """Stop PWM for this motor."""
        self.pwm_in1.stop()
        self.pwm_in2.stop()
        del self.pwm_in1
        del self.pwm_in2

def main():
    # Define motor pins
    in1_pin = 23  # GPIO 23 corresponds to physical pin 16
    in2_pin = 24  # GPIO 24 corresponds to physical pin 18

    # Create motor controller instance
    motor = MotorController(in1_pin, in2_pin)

    try:
        while True:
            cmd = input("Command, f/r 0..9 to move, 's' to stop, 'q' to quit: ")  # Get user input
            if cmd == "q":
                print("Quitting the program.")
                break
            elif cmd == "s":
                motor.stop_motor()
                continue
            elif len(cmd) < 2:
                print("Invalid command. Use format f5, r3, 's' to stop, or 'q' to quit.")
                continue

            direction = cmd[0]
            if direction not in ["f", "r"]:
                print("Invalid direction. Use 'f' for forward or 'r' for reverse.")
                continue

            # Set speed based on the second character of the command
            try:
                speed = int(cmd[1]) * 11  # Convert 0-9 to 0%-99% duty cycle
                motor.set_motor_speed(direction, speed)
            except ValueError:
                print("Invalid speed. Use a number between 0 and 9.")

    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        motor.cleanup()

if __name__ == "__main__":
    main()