import RPi.GPIO as GPIO
import smartcar.src.motor as Motor
from time import sleep

class MotorSystem:
    def __init__(self, motor_pins):
        """Initialize car with a dictionary of motor pins."""
        GPIO.setmode(GPIO.BCM)
        self.motors = []
        for pins in motor_pins:
            self.motors.append(Motor(*pins))  # unpack tuple (IN1, IN2, EN)

    def forward(self, speed=50):
        """Move all motors forward."""
        for motor in self.motors:
            motor.forward(speed)

    def backward(self, speed=50):
        """Move all motors backward."""
        for motor in self.motors:
            motor.backward(speed)

    def turn_left(self, speed=50):
        """Turn left: right motors forward, left motors backward."""
        self.motors[0].backward(speed)  # Front Left
        self.motors[1].backward(speed)  # Rear Left
        self.motors[2].forward(speed)  # Front Right
        self.motors[3].forward(speed)  # Rear Right

    def turn_right(self, speed=50):
        """Turn right: left motors forward, right motors backward."""
        self.motors[0].forward(speed)  # Front Left
        self.motors[1].forward(speed)  # Rear Left
        self.motors[2].backward(speed)  # Front Right
        self.motors[3].backward(speed)  # Rear Right

    def stop(self):
        """Stop all motors."""
        for motor in self.motors:
            motor.stop()

    def cleanup(self):
        """Cleanup GPIO pins."""
        GPIO.cleanup()

# Example test program
if __name__ == "__main__":
    # Example (placeholder) pin assignments (IN1, IN2, EN)
    # NOTE: These will need to be updated to actual assigned pins
    motor_pins = [
        (17, 18, 13),  # Motor 1 (Front Left)
        (22, 23, 12),  # Motor 2 (Rear Left)
        (24, 25, 6),   # Motor 3 (Front Right)
        (27, 4, 5)     # Motor 4 (Rear Right)
    ]

    try:
        motorSystem = MotorSystem(motor_pins)

        print("Moving forward")
        motorSystem.forward(60)
        sleep(2)

        print("Turning left")
        motorSystem.turn_left(60)
        sleep(2)

        print("Turning right")
        motorSystem.turn_right(60)
        sleep(2)

        print("Moving backward")
        motorSystem.backward(60)
        sleep(2)

        print("Stopping")
        motorSystem.stop()

    except KeyboardInterrupt:
        print("\nStopped by user")

    finally:
        motorSystem.cleanup()
