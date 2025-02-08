import pigpio
import RPi.GPIO as GPIO
from time import sleep

class ServoControl:
    def __init__(self, stop_event):
        self.stop_event = stop_event
        self.pi = pigpio.pi()
        if not self.pi.connected:
            print("Failed to connect to pigpio daemon. Please start it with 'sudo pigpiod'.")
            exit()

        self.SERVO_PIN_1 = 22
        self.SERVO_PIN_2 = 18

        self.duty_cycle_1 = 7.5  # Neutral position (90 degrees)
        self.duty_cycle_2 = 7.5  # Neutral position (90 degrees)

        self.pi.set_PWM_frequency(self.SERVO_PIN_1, 50)
        self.pi.set_PWM_frequency(self.SERVO_PIN_2, 50)

        self.BUTTON_UP_1 = 17
        self.BUTTON_DOWN_1 = 27
        self.BUTTON_UP_2 = 5
        self.BUTTON_DOWN_2 = 6
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BUTTON_UP_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.BUTTON_DOWN_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.BUTTON_UP_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.BUTTON_DOWN_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def run(self):
        try:
            print("Starting servo control loop...")
            while not self.stop_event.is_set():
                button_up_state_1 = GPIO.input(self.BUTTON_UP_1)
                button_down_state_1 = GPIO.input(self.BUTTON_DOWN_1)
                button_up_state_2 = GPIO.input(self.BUTTON_UP_2)
                button_down_state_2 = GPIO.input(self.BUTTON_DOWN_2)
                #print(f"Button UP state: {button_up_state_1}, Button DOWN state: {button_down_state_1}")

                # Control servo 1
                if button_up_state_1 == GPIO.HIGH:  # Button pressed
                    self.duty_cycle_1 += 0.1  # Increase duty cycle to turn right
                    if self.duty_cycle_1 > 12.5:  # Limit to +90 deg position
                        self.duty_cycle_1 = 12.5
                    pulse_width_1 = 500 + (self.duty_cycle_1 - 2.5) * 200  # Convert duty cycle to pulse width
                    self.pi.set_servo_pulsewidth(self.SERVO_PIN_1, pulse_width_1)
                    #print(f"Button UP pressed. Duty cycle increased to {self.duty_cycle_1}, pulse width set to {pulse_width_1}")
                elif button_down_state_1 == GPIO.HIGH:  # Button pressed
                    self.duty_cycle_1 -= 0.1  # Decrease duty cycle to turn left
                    if self.duty_cycle_1 < 6:  # Limit to -90 deg position
                        self.duty_cycle_1 = 6
                    pulse_width_1 = 500 + (self.duty_cycle_1 - 2.5) * 200  # Convert duty cycle to pulse width
                    self.pi.set_servo_pulsewidth(self.SERVO_PIN_1, pulse_width_1)
                   # print(f"Button DOWN pressed. Duty cycle decreased to {self.duty_cycle_1}, pulse width set to {pulse_width_1}")

                # Control servo 2
                if button_up_state_2 == GPIO.HIGH:  # Button pressed
                    self.duty_cycle_2 += 0.1  # Increase duty cycle to turn right
                    if self.duty_cycle_2 > 12.5:  # Limit to +90 deg position
                        self.duty_cycle_2 = 12.5
                    pulse_width_2 = 500 + (self.duty_cycle_2 - 2.5) * 200  # Convert duty cycle to pulse width
                    self.pi.set_servo_pulsewidth(self.SERVO_PIN_2, pulse_width_2)
                    #print(f"Button UP pressed. Duty cycle increased to {self.duty_cycle_2}, pulse width set to {pulse_width_2}")
                elif button_down_state_2 == GPIO.HIGH:  # Button pressed
                    self.duty_cycle_2 -= 0.1  # Decrease duty cycle to turn left
                    if self.duty_cycle_2 < 6:  # Limit to -90 deg position
                        self.duty_cycle_2 = 6
                    pulse_width_2 = 500 + (self.duty_cycle_2 - 2.5) * 200  # Convert duty cycle to pulse width
                    self.pi.set_servo_pulsewidth(self.SERVO_PIN_2, pulse_width_2)
                    #print(f"Button DOWN pressed. Duty cycle decreased to {self.duty_cycle_2}, pulse width set to {pulse_width_2}")

                sleep(0.01)  # Small delay to debounce
        finally:
            self.pi.set_servo_pulsewidth(self.SERVO_PIN_1, 0)  # Stop servo 1
            self.pi.set_servo_pulsewidth(self.SERVO_PIN_2, 0)  # Stop servo 2
            GPIO.cleanup()  # Clean up GPIO
            print("Servo control loop stopped and pigpio cleaned up.")

if __name__ == "__main__":
    import threading
    stop_event = threading.Event()
    servo_control = ServoControl(stop_event)
    try:
        servo_control.run()
    except KeyboardInterrupt:
        stop_event.set()