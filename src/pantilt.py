import smbus
import time
import termios
import sys
import tty

class PanTiltController:
    # Constants
    SERVO_UP_CH = 0
    SERVO_DOWN_CH = 1
    SERVO_UP_MAX = 180
    SERVO_UP_MIN = 0
    SERVO_DOWN_MAX = 180
    SERVO_DOWN_MIN = 0
    STEP = 5  # Increase step size for faster movement
    STEP_DELAY = 0.005  # Reduce delay for quicker response

    # PCA9685 Registers
    PCA9685_ADDRESS = 0x40
    MODE1 = 0x00
    PRESCALE = 0xFE
    LED0_ON_L = 0x06

    def __init__(self):
        self.servo_up_degree = 90
        self.servo_down_degree = 90
        self.bus = smbus.SMBus(1)

    def i2c_write_reg(self, addr, reg, data):
        self.bus.write_byte_data(addr, reg, data)

    def i2c_read_reg(self, addr, reg):
        return self.bus.read_byte_data(addr, reg)

    def pca9685_reset(self):
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.MODE1, 0x00)

    def pca9685_set_pwm_freq(self, freq):
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
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * num, on & 0xFF)
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * num + 1, on >> 8)
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * num + 2, off & 0xFF)
        self.i2c_write_reg(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * num + 3, off >> 8)

    def set_servo_pulse(self, n, pulse):
        pulselength = 1000.0
        pulselength /= 60.0
        pulselength /= 4096.0
        pulse *= 1000.0
        pulse /= pulselength
        self.pca9685_set_pwm(n, 0, int(pulse))

    def set_servo_degree(self, n, degree):
        if degree >= 180:
            degree = 180
        elif degree <= 0:
            degree = 0
        pulse = (degree + 45) / (90.0 * 1000)
        self.set_servo_pulse(n, pulse)

    def servo_degree_increase(self, channel, step):
        if channel == self.SERVO_UP_CH:
            if self.servo_up_degree >= self.SERVO_UP_MAX:
                self.servo_up_degree = self.SERVO_UP_MAX
            else:
                self.servo_up_degree += step
            print(f"Increasing ServoUpDegree to {self.servo_up_degree}")
            self.set_servo_degree(channel, self.servo_up_degree)
        elif channel == self.SERVO_DOWN_CH:
            if self.servo_down_degree >= self.SERVO_DOWN_MAX:
                self.servo_down_degree = self.SERVO_DOWN_MAX
            else:
                self.servo_down_degree += step
            print(f"Increasing ServoDownDegree to {self.servo_down_degree}")
            self.set_servo_degree(channel, self.servo_down_degree)
        time.sleep(self.STEP_DELAY)

    def servo_degree_decrease(self, channel, step):
        if channel == self.SERVO_UP_CH:
            if self.servo_up_degree <= self.SERVO_UP_MIN + step:
                self.servo_up_degree = self.SERVO_UP_MIN
            else:
                self.servo_up_degree -= step
            print(f"Decreasing ServoUpDegree to {self.servo_up_degree}")
            self.set_servo_degree(channel, self.servo_up_degree)
        elif channel == self.SERVO_DOWN_CH:
            if self.servo_down_degree <= self.SERVO_DOWN_MIN + step:
                self.servo_down_degree = self.SERVO_DOWN_MIN
            else:
                self.servo_down_degree -= step
            print(f"Decreasing ServoDownDegree to {self.servo_down_degree}")
            self.set_servo_degree(channel, self.servo_down_degree)
        time.sleep(self.STEP_DELAY)

    def process_keyboard_event(self):
        while True:
            time.sleep(0.1)
            key_val = self.get_key_board_from_termios()
            if key_val == '\x1b':
                key_val = self.get_key_board_from_termios()
                if key_val == '[':
                    key_val = self.get_key_board_from_termios()
                    if key_val == 'A':
                        self.servo_degree_increase(self.SERVO_UP_CH, self.STEP)
                    elif key_val == 'B':
                        self.servo_degree_decrease(self.SERVO_UP_CH, self.STEP)
                    elif key_val == 'C':
                        self.servo_degree_increase(self.SERVO_DOWN_CH, self.STEP)
                    elif key_val == 'D':
                        self.servo_degree_decrease(self.SERVO_DOWN_CH, self.STEP)

    def get_key_board_from_termios(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def test(self):
        print("Initializing PCA9685...")
        self.pca9685_reset()
        self.pca9685_set_pwm_freq(60)

        print("Moving all the way to the left")
        while self.servo_down_degree > self.SERVO_DOWN_MIN:
            self.servo_degree_decrease(self.SERVO_DOWN_CH, self.STEP)

        print("Moving all the way to the right")
        while self.servo_down_degree < self.SERVO_DOWN_MAX:
            self.servo_degree_increase(self.SERVO_DOWN_CH, self.STEP)

        print("Moving all the way down")
        while self.servo_up_degree > self.SERVO_UP_MIN:
            self.servo_degree_decrease(self.SERVO_UP_CH, self.STEP)

        print("Moving all the way up")
        while self.servo_up_degree < self.SERVO_UP_MAX:
            self.servo_degree_increase(self.SERVO_UP_CH, self.STEP)

    def initialize_to_middle(self):
        """
        Initialize the pan-tilt mechanism and move it to the middle point.
        """
        print("Initializing PCA9685 and moving to the middle point...")
        self.pca9685_reset()
        self.pca9685_set_pwm_freq(60)

        # Calculate middle points
        self.servo_up_degree = (self.SERVO_UP_MAX + self.SERVO_UP_MIN) // 2
        self.servo_down_degree = (self.SERVO_DOWN_MAX + self.SERVO_DOWN_MIN) // 2

        # Move servos to the middle point
        self.set_servo_degree(self.SERVO_UP_CH, self.servo_up_degree)
        self.set_servo_degree(self.SERVO_DOWN_CH, self.servo_down_degree)

        print(f"Moved to middle point: ServoUpDegree={self.servo_up_degree}, ServoDownDegree={self.servo_down_degree}")


if __name__ == "__main__":
    controller = PanTiltController()
    controller.initialize_to_middle()  # Initialize and move to the middle
    controller.test()  # Run the default behavior