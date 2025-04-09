from jmotor import MotorController
import RPi.GPIO as io
import time

class MovementController:
    def __init__(self):
        """Initialize the movement controller with two motors."""
        # Motor 1 (left motor) uses GPIO 24 and 23
        self.motor1 = MotorController(in1_pin=24, in2_pin=23)
        # Motor 2 (right motor) uses GPIO 27 and 22
        self.motor2 = MotorController(in1_pin=27, in2_pin=22)
        self.cleaned_up = False  # Track if cleanup has been called

    def move_forward(self, speed):
        """Move both motors forward at the specified speed."""
        print(f"Moving forward at {speed}% speed.")
        self.motor1.set_motor_speed(direction="f", duty=speed)
        self.motor2.set_motor_speed(direction="f", duty=speed)

    def move_backward(self, speed):
        """Move both motors backward at the specified speed."""
        print(f"Moving backward at {speed}% speed.")
        self.motor1.set_motor_speed(direction="r", duty=speed)
        self.motor2.set_motor_speed(direction="r", duty=speed)

    def turn_left(self, speed):
        """Turn left by stopping the left motor and running the right motor forward."""
        print(f"Turning left at {speed}% speed.")
        self.motor1.set_motor_speed(direction="f", duty=0)  # Stop left motor
        self.motor2.set_motor_speed(direction="f", duty=speed)  # Run right motor forward

    def turn_right(self, speed):
        """Turn right by stopping the right motor and running the left motor forward."""
        print(f"Turning right at {speed}% speed.")
        self.motor1.set_motor_speed(direction="f", duty=speed)  # Run left motor forward
        self.motor2.set_motor_speed(direction="f", duty=0)  # Stop right motor

    def stop(self):
        """Stop both motors."""
        print("Stopping all motors.")
        self.motor1.stop_motor()
        self.motor2.stop_motor()

    def cleanup(self):
        """Clean up both motors and GPIO."""
        if not self.cleaned_up:  # Ensure cleanup is only called once
            print("Cleaning up all motors and GPIO.")
            self.motor1.stop_pwm()
            self.motor2.stop_pwm()
            io.cleanup()  # Perform GPIO cleanup once
            self.cleaned_up = True
        else:
            print("Cleanup already performed.")

# Example usage
if __name__ == "__main__":
    movement = MovementController()
    try:
        movement.move_forward(100)  # Move forward at 100% speed
        time.sleep(2)
        movement.turn_left(100)  # Turn left at 100% speed
        time.sleep(2)
        movement.move_backward(100)  # Move backward at 100% speed
        time.sleep(2)
        movement.turn_right(100)  # Turn right at 100% speed
        time.sleep(2)
        movement.stop()  # Stop all motors
    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        movement.cleanup()  # Ensure cleanup is called