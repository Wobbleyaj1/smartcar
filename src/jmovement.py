from jmotor import MotorController
import RPi.GPIO as io
import time

io.setwarnings(False)

class MovementController:
    def __init__(self):
        """
        Initialize the movement controller with two motors.
        Motor 1 (left motor) and Motor 2 (right motor) are controlled independently.
        """
        self.motor1 = MotorController(in1_pin=24, in2_pin=23, en1_pin=25)
        self.motor2 = MotorController(in1_pin=27, in2_pin=22, en1_pin=25)

    def move_forward(self, speed):
        """
        Move both motors forward at the specified speed.
        
        Args:
            speed (int): Speed as a percentage (0-100).
        """
        #print(f"Moving forward at {speed}% speed.")
        self.motor1.set_motor_speed(direction="f", duty=speed)
        self.motor2.set_motor_speed(direction="f", duty=speed)

    def move_backward(self, speed):
        """
        Move both motors backward at the specified speed.
        
        Args:
            speed (int): Speed as a percentage (0-100).
        """
        #print(f"Moving backward at {speed}% speed.")
        self.motor1.set_motor_speed(direction="r", duty=speed)
        self.motor2.set_motor_speed(direction="r", duty=speed)

    def turn_left(self, speed):
        """
        Turn left by running the right motor forward and stopping the left motor.
        
        Args:
            speed (int): Speed as a percentage (0-100).
        """
        #print(f"Turning left at {speed}% speed.")
        self.motor1.set_motor_speed(direction="f", duty=speed)
        self.motor2.set_motor_speed(direction="r", duty=speed)

    def turn_right(self, speed):
        """
        Turn right by running the left motor forward and stopping the right motor.
        
        Args:
            speed (int): Speed as a percentage (0-100).
        """
        #print(f"Turning right at {speed}% speed.")
        self.motor1.set_motor_speed(direction="r", duty=speed)
        self.motor2.set_motor_speed(direction="f", duty=speed)

    def stop(self):
        """
        Stop both motors by setting their speed to 0.
        """
        #print("Stopping all motors.")
        self.motor1.stop_motor()
        self.motor2.stop_motor()

    def cleanup(self):
        """
        Clean up both motors.
        """
        #print("Cleaning up all motors.")
        self.motor1.stop_motor()
        self.motor2.stop_motor()
        io.cleanup()

if __name__ == "__main__":
    """
    Example main function to control the movement using predefined directions.
    """
    movement = MovementController()
    try:
        time.sleep(1)
        movement.move_forward(100)
        time.sleep(1)
        movement.turn_left(100)
        time.sleep(1)
        movement.move_backward(100)
        time.sleep(1)
        movement.turn_right(100)
        time.sleep(1)
        movement.stop()
    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        movement.cleanup()