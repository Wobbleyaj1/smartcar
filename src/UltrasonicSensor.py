from gpiozero import DistanceSensor

ultrasonic = DistanceSensor(echo=17, trigger=4, threshold_distance=0.2)
while True:
    ultrasonic.wait_for_out_of_range()
        # Go car
    ultrasonic.wait_for_in_range()
        # Stop car