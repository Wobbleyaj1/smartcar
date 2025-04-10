from ultrasonic_sensor import HCSR04
from object_tracker import ObjectTracker
from jmovement import MovementController
import time
import threading

class SmartCarSystem:
    def __init__(self):
        self.ultrasonic_sensor = HCSR04(trigger_pin=17, echo_pin=18)
        self.movement_controller = MovementController()
        self.object_tracker = ObjectTracker(model_path="yolov5nu_ncnn_model", object="person")
        self.distance = None
        self.frame_centered = False
        self.running = True

    def ultrasonic_thread(self):
        while self.running:
            self.distance = self.ultrasonic_sensor.get_distance()
            print(f"Distance: {self.distance} cm")
            time.sleep(0.1)

    def object_tracking_thread(self):
        while self.running:
            self.frame_centered = self.object_tracker.track_object()
            time.sleep(0.1)

    def movement_thread(self):
        was_stopped = False
        while self.running:
            if self.distance is not None:
                if self.distance < 20:
                    if not was_stopped:
                        print("Obstacle detected! Stopping motors.")
                        self.movement_controller.stop()
                        was_stopped = True
                else:
                    if self.frame_centered:
                        print("Object centered. Moving forward.")
                        self.movement_controller.move_forward(50)  # Move forward at 50% speed
                    else:
                        print("Object not centered. Adjusting position.")
                        pan_angle = self.object_tracker.pan_tilt.get_pan_angle()
                        if pan_angle > 10:  # Object is to the right
                            print("Object is to the right. Turning right.")
                            self.movement_controller.turn_right(30)  # Turn right at 30% speed
                        elif pan_angle < -10:  # Object is to the left
                            print("Object is to the left. Turning left.")
                            self.movement_controller.turn_left(30)  # Turn left at 30% speed
                        else:
                            print("Object is roughly centered. Stopping to adjust pan-tilt.")
                            self.movement_controller.stop()
            time.sleep(0.1)

    def cleanup(self):
        self.ultrasonic_sensor.cleanup()
        self.movement_controller.cleanup()
        print("System cleanup complete.")

def main():
    smart_car = SmartCarSystem()

    # Create threads for each system
    ultrasonic_thread = threading.Thread(target=smart_car.ultrasonic_thread, daemon=True)
    tracking_thread = threading.Thread(target=smart_car.object_tracking_thread, daemon=True)
    movement_thread = threading.Thread(target=smart_car.movement_thread, daemon=True)

    try:
        print("Smart car system initialized. Starting threads...")
        # Start threads
        ultrasonic_thread.start()
        tracking_thread.start()
        movement_thread.start()

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nExiting program.")
        smart_car.running = False
        ultrasonic_thread.join()
        tracking_thread.join()
        movement_thread.join()
    finally:
        smart_car.cleanup()

if __name__ == "__main__":
    main()