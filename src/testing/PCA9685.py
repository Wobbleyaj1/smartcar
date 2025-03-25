import smbus
import time
import sys
import tty
import termios

# PCA9685 Registers
PCA9685_ADDRESS = 0x40
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

# Servo Limits
SERVO_MIN = 150  # Minimum pulse length out of 4096
SERVO_MAX = 600  # Maximum pulse length out of 4096

class PCA9685:
    def __init__(self, address=PCA9685_ADDRESS, bus=1):
        self.address = address
        self.bus = smbus.SMBus(bus)
        self.reset()
        self.set_pwm_freq(50)

    def reset(self):
        self.bus.write_byte_data(self.address, MODE1, 0x00)

    def set_pwm_freq(self, freq_hz):
        prescale_val = int(25000000.0 / (4096 * freq_hz) - 1)
        old_mode = self.bus.read_byte_data(self.address, MODE1)
        new_mode = (old_mode & 0x7F) | 0x10  # Sleep mode
        self.bus.write_byte_data(self.address, MODE1, new_mode)
        self.bus.write_byte_data(self.address, PRESCALE, prescale_val)
        self.bus.write_byte_data(self.address, MODE1, old_mode)
        time.sleep(0.005)
        self.bus.write_byte_data(self.address, MODE1, old_mode | 0xA1)

    def set_pwm(self, channel, on, off):
        self.bus.write_byte_data(self.address, LED0_ON_L + 4 * channel, on & 0xFF)
        self.bus.write_byte_data(self.address, LED0_ON_L + 4 * channel + 1, on >> 8)
        self.bus.write_byte_data(self.address, LED0_ON_L + 4 * channel + 2, off & 0xFF)
        self.bus.write_byte_data(self.address, LED0_ON_L + 4 * channel + 3, off >> 8)

    def set_servo_angle(self, channel, angle):
        pulse_length = SERVO_MIN + (angle / 180.0) * (SERVO_MAX - SERVO_MIN)
        self.set_pwm(channel, 0, int(pulse_length))

# Function to read keyboard input
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

if __name__ == "__main__":
    pca9685 = PCA9685()
    angle = 90  # Start at neutral position

    print("Use 'a' and 'd' to control the servo angle. Press 'q' to quit.")
    
    while True:
        key = get_key()
        if key == 'a':
            angle = max(0, angle - 10)
        elif key == 'd':
            angle = min(180, angle + 10)
        elif key == 'q':
            break
        print(f"Setting angle: {angle}")
        pca9685.set_servo_angle(0, angle)
        time.sleep(0.1)
