import RPi.GPIO as GPIO
from motor import Motor 
from time import sleep

class MotorSystem:
    def __init__(self, motor_pins):
        """Initialize car with a list of motor pin tuples."""
        GPIO.setmode(GPIO.BCM)
        self.motors = []
        for pins in motor_pins:
            self.motors.append(Motor(*pins))  # Unpack tuple (IN1, IN2, EN)

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
    # Define GPIO pins for motor control
    # Define GPIO pins for motor control
    MOTOR_PINS = {
        "EN1": 3, "IN1": 5, "IN2": 7,       # Motor 1
        "EN2": 29, "IN3": 31, "IN4": 26,    # Motor 2
        "EN3": 24, "IN5": 21, "IN6": 19,    # Motor 3
        "EN4": 23, "IN7": 32, "IN8": 33     # Motor 4
    }

    motor_pins = [
        ("EN1", "IN1", "IN2"),      # Motor 1 (Front Left)
        ("EN2", "IN3", "IN4"),      # Motor 2 (Rear Left)
        ("EN3", "IN5", "IN6"),      # Motor 3 (Front Right)
        ("EN4", "IN7", "IN8")       # Motor 4 (Rear Right)
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

