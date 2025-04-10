import RPi.GPIO as io

class MotorController:
    def __init__(self, in1_pin, in2_pin, en1_pin=None, frequency=500):
        """
        Initialize the motor controller.
        
        Args:
            in1_pin (int): GPIO pin for motor input 1.
            in2_pin (int): GPIO pin for motor input 2.
            en1_pin (int, optional): GPIO pin for motor enable. Defaults to None.
            frequency (int): PWM frequency in Hz. Defaults to 500.
        """
        self.in1_pin = in1_pin
        self.in2_pin = in2_pin
        self.en1_pin = en1_pin
        self.frequency = frequency

        io.setmode(io.BCM)
        io.setup(self.in1_pin, io.OUT)
        io.setup(self.in2_pin, io.OUT)
        if self.en1_pin is not None:
            io.setup(self.en1_pin, io.OUT)
            io.output(self.en1_pin, io.HIGH)

        self.pwm_in1 = io.PWM(self.in1_pin, self.frequency)
        self.pwm_in2 = io.PWM(self.in2_pin, self.frequency)
        self.pwm_in1.start(0)
        self.pwm_in2.start(0)

    def set_motor_speed(self, direction, duty):
        """
        Set the motor speed and direction.
        
        Args:
            direction (str): 'f' for forward, 'r' for reverse.
            duty (int): Duty cycle percentage (0-100).
        """
        #print(f"Setting motor to {'forward' if direction == 'f' else 'reverse'} at {duty}% duty cycle")
        if direction == "f":
            self.pwm_in1.ChangeDutyCycle(duty)
            self.pwm_in2.ChangeDutyCycle(0)
        elif direction == "r":
            self.pwm_in1.ChangeDutyCycle(0)
            self.pwm_in2.ChangeDutyCycle(duty)

    def stop_motor(self):
        """Stop the motor by setting both PWM duty cycles to 0."""
        self.pwm_in1.ChangeDutyCycle(0)
        self.pwm_in2.ChangeDutyCycle(0)
        
if __name__ == "__main__":
    """
    Example main function to control the motor using user input.
    """
    in1_pin = 23  # GPIO 23 corresponds to physical pin 16
    in2_pin = 24  # GPIO 24 corresponds to physical pin 18
    en1_pin = 25  # GPIO 25 corresponds to physical pin 22

    motor = MotorController(in1_pin, in2_pin, en1_pin)

    try:
        while True:
            cmd = input("Command, f/r 0..9 to move, 's' to stop, 'q' to quit: ")
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

            try:
                speed = int(cmd[1]) * 11  # Convert 0-9 to 0%-99% duty cycle
                motor.set_motor_speed(direction, speed)
            except ValueError:
                print("Invalid speed. Use a number between 0 and 9.")

    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        motor.stop_motor()

io.cleanup()