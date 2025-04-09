import RPi.GPIO as GPIO
import motor as Motor
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


'''
    # Setup GPIO
    GPIO.setmode(GPIO.BCM)
    for pin in MOTOR_PINS.values():
        GPIO.setup(pin, GPIO.OUT)

    # Create PWM objects for motor speed control
    pwm_EN1 = GPIO.PWM(MOTOR_PINS["EN1"], 1000)
    pwm_EN2 = GPIO.PWM(MOTOR_PINS["EN2"], 1000)
    pwm_EN3 = GPIO.PWM(MOTOR_PINS["EN3"], 1000)
    pwm_EN4 = GPIO.PWM(MOTOR_PINS["EN4"], 1000)

    pwm_EN1.start(0)
    pwm_EN2.start(0)
    pwm_EN3.start(0)
    pwm_EN4.start(0)

    # Function to control a motor
    def set_motor(motor, direction, speed):
        if motor == 1:
            IN1, IN2, EN = MOTOR_PINS["IN1"], MOTOR_PINS["IN2"], pwm_EN1
        elif motor == 2:
            IN1, IN2, EN = MOTOR_PINS["IN3"], MOTOR_PINS["IN4"], pwm_EN2
        elif motor == 3:
            IN1, IN2, EN = MOTOR_PINS["IN5"], MOTOR_PINS["IN6"], pwm_EN3
        elif motor == 4:
            IN1, IN2, EN = MOTOR_PINS["IN7"], MOTOR_PINS["IN8"], pwm_EN4
        else:
            return
        
        # Set direction
        if direction == "forward":
            GPIO.output(IN1, GPIO.HIGH)
            GPIO.output(IN2, GPIO.LOW)
        elif direction == "backward":
            GPIO.output(IN1, GPIO.LOW)
            GPIO.output(IN2, GPIO.HIGH)
        else:
            GPIO.output(IN1, GPIO.LOW)
            GPIO.output(IN2, GPIO.LOW)

        # Set speed
        EN.ChangeDutyCycle(speed)

    # Test Motor 1
    set_motor(1, "forward", 50)  # 50% speed forward
    time.sleep(2)
    set_motor(1, "backward", 50)  # 50% speed backward
    time.sleep(2)
    set_motor(1, "stop", 0)

    # Cleanup
    GPIO.cleanup()

'''

