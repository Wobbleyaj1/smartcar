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
        self.running = True

    def ultrasonic_thread(self):
        try:
            while self.running:
                self.distance = self.ultrasonic_sensor.get_distance()
                if self.distance > 10:
                    print(f"Distance: {self.distance} cm")
                time.sleep(0.1)
        finally:
            print("Ultrasonic thread exiting...")

    def object_tracking_thread(self):
        try:
            while self.running:
                self.object_tracker.track_object()
                time.sleep(0.1)
        finally:
            print("Object tracking thread exiting...")

    def movement_thread(self):
        was_stopped = False
        try:
            while self.running:
                if self.distance is not None:
                    if self.distance < 10:
                        if not was_stopped:
                            print("Obstacle detected! Stopping motors.")
                            was_stopped = True
                            self.movement_controller.stop()
                    else:
                            if was_stopped:
                                print("Obstacle cleared. Resuming movement.")
                                was_stopped = False
                            print("Object not centered. Adjusting position.")
                            pan_angle = self.object_tracker.pan_tilt.get_pan_angle()
                            print(f"Pan angle: {pan_angle} degrees")
                            if pan_angle > 25:  # Object is to the right
                                print("Object is to the right. Turning right.")
                                self.movement_controller.stop()
                                self.movement_controller.turn_right(100)  # Turn right at 100% speed  
                                time.sleep(0.1)  # Pause briefly to reset
                            elif pan_angle < 0:  # Object is to the left
                                print("Object is to the left. Turning left.")
                                self.movement_controller.stop()
                                self.movement_controller.turn_left(100)  # Turn left at 100% speed
                                time.sleep(0.1)  # Pause briefly to reset
                            else:
                                print("Object centered. Moving forward.")
                                self.movement_controller.stop()
                                self.movement_controller.move_forward(100)  # Move forward at 60% speed
                                time.sleep(0.1)  # Pause briefly to reset
                                
                time.sleep(0.1)
        finally:
            print("Movement thread exiting...")

    def cleanup(self):
        print("Cleaning up resources...")
        try:
            self.ultrasonic_sensor.cleanup()
            self.movement_controller.cleanup()
        except Exception as e:
            print(f"Error during cleanup: {e}")
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
        ultrasonic_thread.join(timeout=1)
        tracking_thread.join(timeout=1)
        movement_thread.join(timeout=1)
    finally:
        smart_car.cleanup()

if __name__ == "__main__":
    main()