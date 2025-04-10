import smbus
import time
import termios
import sys
import tty

class PanTiltController:
    # Constants
    SERVO_TILT_CH = 0  # Channel for the tilt (up/down) servo
    SERVO_PAN_CH = 1  # Channel for the pan (left/right) servo
    SERVO_TILT_MAX = 180  # Maximum tilt angle
    SERVO_TILT_MIN = 0  # Minimum tilt angle
    SERVO_PAN_MAX = 180  # Maximum pan angle
    SERVO_PAN_MIN = 0  # Minimum pan angle
    STEP = 1  # Step size for slower movement
    STEP_DELAY = 0.02  # Delay after each movement

    # PCA9685 Registers
    PCA9685_ADDRESS = 0x40
    MODE1 = 0x00
    PRESCALE = 0xFE
    LED0_ON_L = 0x06

    def __init__(self):
        # Initialize servo positions to middle
        self.servo_tilt_degree = 90
        self.servo_pan_degree = 90
        # Initialize I2C bus
        self.bus = smbus.SMBus(1)
        # Initialize pan angle
        self.pan_angle = 0  

    def i2c_write_reg(self, addr, reg, data):
        """Write a byte to a specific register over I2C."""
        self.bus.write_byte_data(addr, reg, data)

    def i2c_read_reg(self, addr, reg):
        """Read a byte from a specific register over I2C."""
        return self.bus.read_byte_data(addr, reg)

    def pca9685_reset(self):
        """Reset the PCA9685 module."""
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.MODE1, 0x00)

    def pca9685_set_pwm_freq(self, freq):
        """Set the PWM frequency for the PCA9685."""
        prescaleval = 25000000.0
        prescaleval /= 4096.0
        prescaleval /= freq
        prescaleval -= 1.0
        prescale = int(prescaleval + 0.5)
        oldmode = self.i2c_read_reg(self.PCA9685_ADDRESS, self.MODE1)
        newmode = (oldmode & 0x7F) | 0x10  # Sleep mode
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.MODE1, newmode)
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.PRESCALE, prescale)
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.MODE1, oldmode)
        time.sleep(0.005)
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.MODE1, oldmode | 0xA1)

    def pca9685_set_pwm(self, num, on, off):
        """Set the PWM signal for a specific channel."""
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * num, on & 0xFF)
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * num + 1, on >> 8)
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * num + 2, off & 0xFF)
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * num + 3, off >> 8)

    def set_servo_pulse(self, n, pulse):
        """Set the servo pulse width."""
        pulselength = 1000.0
        pulselength /= 60.0
        pulselength /= 4096.0
        pulse *= 1000.0
        pulse /= pulselength
        self.pca9685_set_pwm(n, 0, int(pulse))

    def set_servo_degree(self, n, degree):
        """Set the servo to a specific angle."""
        if degree >= 180:
            degree = 180
        elif degree <= 0:
            degree = 0
        pulse = (degree + 45) / (90.0 * 1000)
        self.set_servo_pulse(n, pulse)

    def servo_degree_increase(self, channel, step):
        """Increase the servo angle by a step."""
        if channel == self.SERVO_TILT_CH:
            if self.servo_tilt_degree >= self.SERVO_TILT_MAX:
                self.servo_tilt_degree = self.SERVO_TILT_MAX
            else:
                self.servo_tilt_degree += step
            self.set_servo_degree(channel, self.servo_tilt_degree)
        elif channel == self.SERVO_PAN_CH:
            if self.servo_pan_degree >= self.SERVO_PAN_MAX:
                self.servo_pan_degree = self.SERVO_PAN_MAX
            else:
                self.servo_pan_degree += step
                self.pan_angle += step  # Update pan_angle
            self.set_servo_degree(channel, self.servo_pan_degree)
        time.sleep(self.STEP_DELAY)

    def servo_degree_decrease(self, channel, step):
        """Decrease the servo angle by a step."""
        if channel == self.SERVO_TILT_CH:
            if self.servo_tilt_degree <= self.SERVO_TILT_MIN + step:
                self.servo_tilt_degree = self.SERVO_TILT_MIN
            else:
                self.servo_tilt_degree -= step
            self.set_servo_degree(channel, self.servo_tilt_degree)
        elif channel == self.SERVO_PAN_CH:
            if self.servo_pan_degree <= self.SERVO_PAN_MIN + step:
                self.servo_pan_degree = self.SERVO_PAN_MIN
            else:
                self.servo_pan_degree -= step
                self.pan_angle -= step  # Update pan_angle
            self.set_servo_degree(channel, self.servo_pan_degree)
        time.sleep(self.STEP_DELAY)

    def get_key_board_from_termios(self):
        """Read a single character from the keyboard."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    def process_keyboard_event(self):
        """Process keyboard input to control the servos."""
        while True:
            time.sleep(0.1)
            key_val = self.get_key_board_from_termios()
            if key_val == '\x1b':
                key_val = self.get_key_board_from_termios()
                if key_val == '[':
                    key_val = self.get_key_board_from_termios()
                    if key_val == 'A':
                        self.servo_degree_increase(self.SERVO_TILT_CH, self.STEP)
                    elif key_val == 'B':
                        self.servo_degree_decrease(self.SERVO_TILT_CH, self.STEP)
                    elif key_val == 'C':
                        self.servo_degree_increase(self.SERVO_PAN_CH, self.STEP)
                    elif key_val == 'D':
                        self.servo_degree_decrease(self.SERVO_PAN_CH, self.STEP)

    def get_pan_angle(self):
        return self.pan_angle
    
    def initialize_to_middle(self):
        """
        Initialize the pan-tilt mechanism and move it to the middle point.
        """
        #print("Initializing PCA9685 and moving to the middle point...")
        self.pca9685_reset()
        self.pca9685_set_pwm_freq(60)

        # Calculate middle points
        self.servo_tilt_degree = (self.SERVO_TILT_MAX + self.SERVO_TILT_MIN) // 2 + 60  # Adjusted for better visibility
        self.servo_pan_degree = (self.SERVO_PAN_MAX + self.SERVO_PAN_MIN) // 2

        # Move servos to the middle point
        self.set_servo_degree(self.SERVO_TILT_CH, self.servo_tilt_degree)
        self.set_servo_degree(self.SERVO_PAN_CH, self.servo_pan_degree)

        #print(f"Moved to middle point: ServoUpDegree={self.servo_tilt_degree}, ServoDownDegree={self.servo_pan_degree}")


if __name__ == "__main__":
    """
    Example main function to control the pantilt module.
    """
    controller = PanTiltController()
    controller.initialize_to_middle()

    print("Moving all the way to the left")
    while controller.servo_pan_degree > controller.SERVO_PAN_MIN:
        controller.servo_degree_decrease(controller.SERVO_PAN_CH, controller.STEP)

    print("Moving all the way to the right")
    while controller.servo_pan_degree < controller.SERVO_PAN_MAX:
        controller.servo_degree_increase(controller.SERVO_PAN_CH, controller.STEP)

    print("Moving all the way down")
    while controller.servo_tilt_degree > controller.SERVO_TILT_MIN:
        controller.servo_degree_decrease(controller.SERVO_TILT_CH, controller.STEP)

    print("Moving all the way up")
    while controller.servo_tilt_degree < controller.SERVO_TILT_MAX:
        controller.servo_degree_increase(controller.SERVO_TILT_CH, controller.STEP)