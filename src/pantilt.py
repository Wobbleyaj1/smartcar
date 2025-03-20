import smbus
import time
import termios
import sys
import tty

# Constants
SERVO_UP_CH = 0
SERVO_DOWN_CH = 1
SERVO_UP_MAX = 180
SERVO_UP_MIN = 0
SERVO_DOWN_MAX = 180
SERVO_DOWN_MIN = 0
STEP = 1
STEP_DELAY = 0.01

# PCA9685 Registers
PCA9685_ADDRESS = 0x40
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

# Global variables
ServoUpDegree = 90
ServoDownDegree = 90

# I2C bus
bus = smbus.SMBus(1)

def i2c_writeReg(addr, reg, data):
    bus.write_byte_data(addr, reg, data)

def i2c_readReg(addr, reg):
    return bus.read_byte_data(addr, reg)

def PCA9685_reset():
    i2c_writeReg(PCA9685_ADDRESS, MODE1, 0x00)

def PCA9685_setPWMFreq(freq):
    prescaleval = 25000000.0
    prescaleval /= 4096.0
    prescaleval /= freq
    prescaleval -= 1.0
    prescale = int(prescaleval + 0.5)
    oldmode = i2c_readReg(PCA9685_ADDRESS, MODE1)
    newmode = (oldmode & 0x7F) | 0x10  # Sleep mode
    i2c_writeReg(PCA9685_ADDRESS, MODE1, newmode)
    i2c_writeReg(PCA9685_ADDRESS, PRESCALE, prescale)
    i2c_writeReg(PCA9685_ADDRESS, MODE1, oldmode)
    time.sleep(0.005)
    i2c_writeReg(PCA9685_ADDRESS, MODE1, oldmode | 0xA1)

def PCA9685_setPWM(num, on, off):
    i2c_writeReg(PCA9685_ADDRESS, LED0_ON_L + 4 * num, on & 0xFF)
    i2c_writeReg(PCA9685_ADDRESS, LED0_ON_L + 4 * num + 1, on >> 8)
    i2c_writeReg(PCA9685_ADDRESS, LED0_ON_L + 4 * num + 2, off & 0xFF)
    i2c_writeReg(PCA9685_ADDRESS, LED0_ON_L + 4 * num + 3, off >> 8)

def setServoPulse(n, pulse):
    pulselength = 1000.0
    pulselength /= 60.0
    pulselength /= 4096.0
    pulse *= 1000.0
    pulse /= pulselength
    PCA9685_setPWM(n, 0, int(pulse))

def setServoDegree(n, Degree):
    if Degree >= 180:
        Degree = 180
    elif Degree <= 0:
        Degree = 0
    pulse = (Degree + 45) / (90.0 * 1000)
    setServoPulse(n, pulse)

def get_key_board_from_termios():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def ServoDegreeIncrease(Channel, Step):
    global ServoUpDegree, ServoDownDegree
    if Channel == SERVO_UP_CH:
        if ServoUpDegree >= SERVO_UP_MAX:
            ServoUpDegree = SERVO_UP_MAX
        else:
            ServoUpDegree += Step
        print(f"Increasing ServoUpDegree to {ServoUpDegree}")
        setServoDegree(Channel, ServoUpDegree)
    elif Channel == SERVO_DOWN_CH:
        if ServoDownDegree >= SERVO_DOWN_MAX:
            ServoDownDegree = SERVO_DOWN_MAX
        else:
            ServoDownDegree += Step
        print(f"Increasing ServoDownDegree to {ServoDownDegree}")
        setServoDegree(Channel, ServoDownDegree)
    time.sleep(STEP_DELAY)

def ServoDegreeDecrease(Channel, Step):
    global ServoUpDegree, ServoDownDegree
    if Channel == SERVO_UP_CH:
        if ServoUpDegree <= SERVO_UP_MIN + Step:
            ServoUpDegree = SERVO_UP_MIN
        else:
            ServoUpDegree -= Step
        print(f"Decreasing ServoUpDegree to {ServoUpDegree}")
        setServoDegree(Channel, ServoUpDegree)
    elif Channel == SERVO_DOWN_CH:
        if ServoDownDegree <= SERVO_DOWN_MIN + Step:
            ServoDownDegree = SERVO_DOWN_MIN
        else:
            ServoDownDegree -= Step
        print(f"Decreasing ServoDownDegree to {ServoDownDegree}")
        setServoDegree(Channel, ServoDownDegree)
    time.sleep(STEP_DELAY)

def processKeyboardEvent():
    while True:
        time.sleep(0.1)
        keyVal = get_key_board_from_termios()
        if keyVal == '\x1b':
            keyVal = get_key_board_from_termios()
            if keyVal == '[':
                keyVal = get_key_board_from_termios()
                if keyVal == 'A':
                    ServoDegreeIncrease(SERVO_UP_CH, STEP)
                elif keyVal == 'B':
                    ServoDegreeDecrease(SERVO_UP_CH, STEP)
                elif keyVal == 'C':
                    ServoDegreeIncrease(SERVO_DOWN_CH, STEP)
                elif keyVal == 'D':
                    ServoDegreeDecrease(SERVO_DOWN_CH, STEP)

def main():
    print("Initializing PCA9685...")
    PCA9685_reset()  # Reset the PCA9685
    PCA9685_setPWMFreq(60)  # Set frequency to 60 Hz

    print("Moving all the way to the left")
    while ServoDownDegree > SERVO_DOWN_MIN:
        ServoDegreeDecrease(SERVO_DOWN_CH, STEP)

    print("Moving all the way to the right")
    while ServoDownDegree < SERVO_DOWN_MAX:
        ServoDegreeIncrease(SERVO_DOWN_CH, STEP)

    print("Moving all the way down")
    while ServoUpDegree > SERVO_UP_MIN:
        ServoDegreeDecrease(SERVO_UP_CH, STEP)

    print("Moving all the way up")
    while ServoUpDegree < SERVO_UP_MAX:
        ServoDegreeIncrease(SERVO_UP_CH, STEP)

if __name__ == "__main__":
    main()
