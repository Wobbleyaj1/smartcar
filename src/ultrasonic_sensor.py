import RPi.GPIO as GPIO
import time

class HCSR04:
    def __init__(self, trigger_pin, echo_pin):
        """
        Initialize the HCSR04 ultrasonic sensor.
        
        Args:
            trigger_pin (int): GPIO pin connected to the sensor's trigger pin.
            echo_pin (int): GPIO pin connected to the sensor's echo pin.
        """
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        
        GPIO.output(self.trigger_pin, GPIO.LOW)
        time.sleep(2)
    
    def get_distance(self):
        """
        Measure the distance to an object using the ultrasonic sensor.
        
        Returns:
            float: Distance to the object in centimeters.
        """
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        time.sleep(0.00001) #10 microseconds
        GPIO.output(self.trigger_pin, GPIO.LOW)
        
        # Wait for the echo to start
        while GPIO.input(self.echo_pin) == 0:
            pulse_start = time.time()
        
        # Wait for the echo to end
        while GPIO.input(self.echo_pin) == 1:
            pulse_end = time.time()
        
        # Calculate the duration of the pulse
        pulse_duration = pulse_end - pulse_start
        
        # Calculate the distance (speed of sound is 34300 cm/s)
        distance = pulse_duration * 17150 # Multiply by 34300/2
        distance = round(distance, 2) # Round to 2 decimal places
        
        return distance
    
    def cleanup(self):
        """
        Clean up GPIO resources when the sensor is no longer needed.
        """
        #GPIO.cleanup()

if __name__ == "__main__":
    """
    Example main function to demonstrate the ultrasonic sensor.
    """
    sensor = HCSR04(trigger_pin=24, echo_pin=23)
    try:
        below_threshold = False
        while True:
            distance = sensor.get_distance()
            if distance < 20:
                if not below_threshold:
                    print("Stop")
                    below_threshold = True
            else:
                if below_threshold:
                    below_threshold = False
                print(f"Distance: {distance} cm")
            time.sleep(.1)
    except KeyboardInterrupt:
        print("Measurement stopped by user")
        sensor.cleanup()