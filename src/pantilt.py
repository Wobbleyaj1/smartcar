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
    STEP = 1
    STEP_DELAY = 0.1

    def __init__(self):
        # Global variables
        self.ServoUpDegree = 90
        self.ServoDownDegree = 90

        # I2C bus
        self.bus = smbus.SMBus(1)
        self.PCA9685_ADDRESS = 0x40
        self.PCA9685_MODE1 = 0x00
        self.PCA9685_PRESCALE = 0xFE
        self.LED0_ON_L = 0x06

    def i2c_writeReg(self, addr, reg, data):
        self.bus.write_byte_data(addr, reg, data)

    def i2c_readReg(self, addr, reg):
        return self.bus.read_byte_data(addr, reg)

    def PCA9685_setPWMFreq(self, freq):
        freq *= 0.8449
        prescaleval = 25000000.0
        prescaleval /= 4096.0
        prescaleval /= freq
        prescaleval -= 1.0
        prescale = int(prescaleval + 0.5)
        oldmode = self.i2c_readReg(self.PCA9685_ADDRESS, self.PCA9685_MODE1)
        newmode = (oldmode & 0x7F) | 0x10
        self.i2c_writeReg(self.PCA9685_ADDRESS, self.PCA9685_MODE1, newmode)
        self.i2c_writeReg(self.PCA9685_ADDRESS, self.PCA9685_PRESCALE, prescale)
        self.i2c_writeReg(self.PCA9685_ADDRESS, self.PCA9685_MODE1, oldmode)
        time.sleep(0.005)
        self.i2c_writeReg(self.PCA9685_ADDRESS, self.PCA9685_MODE1, oldmode | 0xA0)

    def PCA9685_setPWM(self, num, on, off):
        self.i2c_writeReg(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * num, on & 0xFF)
        self.i2c_writeReg(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * num + 1, on >> 8)
        self.i2c_writeReg(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * num + 2, off & 0xFF)
        self.i2c_writeReg(self.PCA9685_ADDRESS, self.LED0_ON_L + 4 * num + 3, off >> 8)

    def setServoPulse(self, n, pulse):
        pulselength = 1000.0
        pulselength /= 60.0
        pulselength /= 4096.0
        pulse *= 1000.0
        pulse /= pulselength
        self.PCA9685_setPWM(n, 0, int(pulse))

    def setServoDegree(self, n, Degree):
        if Degree >= 180:
            Degree = 180
        elif Degree <= 0:
            Degree = 0
        pulse = (Degree + 45) / (90.0 * 1000)
        self.setServoPulse(n, pulse)

    def get_key_board_from_termios(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def ServoDegreeIncrease(self, Channel, Step):
        if Channel == self.SERVO_UP_CH:
            if self.ServoUpDegree >= self.SERVO_UP_MAX:
                self.ServoUpDegree = self.SERVO_UP_MAX
            else:
                self.ServoUpDegree += Step
            print(f"Increasing ServoUpDegree to {self.ServoUpDegree}")
            self.setServoDegree(Channel, self.ServoUpDegree)
        elif Channel == self.SERVO_DOWN_CH:
            if self.ServoDownDegree >= self.SERVO_DOWN_MAX:
                self.ServoDownDegree = self.SERVO_DOWN_MAX
            else:
                self.ServoDownDegree += Step
            print(f"Increasing ServoDownDegree to {self.ServoDownDegree}")
            self.setServoDegree(Channel, self.ServoDownDegree)
        time.sleep(self.STEP_DELAY)

    def ServoDegreeDecrease(self, Channel, Step):
        if Channel == self.SERVO_UP_CH:
            if self.ServoUpDegree <= self.SERVO_UP_MIN + Step:
                self.ServoUpDegree = self.SERVO_UP_MIN
            else:
                self.ServoUpDegree -= Step
            print(f"Decreasing ServoUpDegree to {self.ServoUpDegree}")
            self.setServoDegree(Channel, self.ServoUpDegree)
        elif Channel == self.SERVO_DOWN_CH:
            if self.ServoDownDegree <= self.SERVO_DOWN_MIN + Step:
                self.ServoDownDegree = self.SERVO_DOWN_MIN
            else:
                self.ServoDownDegree -= Step
            print(f"Decreasing ServoDownDegree to {self.ServoDownDegree}")
            self.setServoDegree(Channel, self.ServoDownDegree)
        time.sleep(self.STEP_DELAY)

    def processKeyboardEvent(self):
        while True:
            time.sleep(0.1)
            keyVal = self.get_key_board_from_termios()
            if keyVal == '\x1b':
                keyVal = self.get_key_board_from_termios()
                if keyVal == '[':
                    keyVal = self.get_key_board_from_termios()
                    if keyVal == 'A':
                        self.ServoDegreeIncrease(self.SERVO_UP_CH, self.STEP)
                    elif keyVal == 'B':
                        self.ServoDegreeDecrease(self.SERVO_UP_CH, self.STEP)
                    elif keyVal == 'C':
                        self.ServoDegreeIncrease(self.SERVO_DOWN_CH, self.STEP)
                    elif keyVal == 'D':
                        self.ServoDegreeDecrease(self.SERVO_DOWN_CH, self.STEP)

    def run(self):
        print("Setting PWM frequency to 60 Hz")
        self.PCA9685_setPWMFreq(60)  # Set frequency to 60 Hz
        
        print("Moving all the way to the left")
        while self.ServoDownDegree > self.SERVO_DOWN_MIN:
            self.ServoDegreeDecrease(self.SERVO_DOWN_CH, self.STEP)
        
        print("Moving all the way to the right")
        while self.ServoDownDegree < self.SERVO_DOWN_MAX:
            self.ServoDegreeIncrease(self.SERVO_DOWN_CH, self.STEP)
        
        print("Moving all the way down")
        while self.ServoUpDegree > self.SERVO_UP_MIN:
            self.ServoDegreeDecrease(self.SERVO_UP_CH, self.STEP)
        
        print("Moving all the way up")
        while self.ServoUpDegree < self.SERVO_UP_MAX:
            self.ServoDegreeIncrease(self.SERVO_UP_CH, self.STEP)

if __name__ == "__main__":
    controller = PanTiltController()
    controller.run()