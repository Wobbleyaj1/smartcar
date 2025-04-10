from ultrasonic_sensor import HCSR04
from object_tracker import ObjectTracker
from jmovement import MovementController
import time

def main():
    # Initialize components
    ultrasonic_sensor = HCSR04(trigger_pin=24, echo_pin=23)
    movement_controller = MovementController()
    object_tracker = ObjectTracker(model_path="yolov5nu_ncnn_model", object="person")

    try:
        print("Smart car system initialized. Starting main loop...")
        while True:
            # Check distance using the ultrasonic sensor
            distance = ultrasonic_sensor.get_distance()
            print(f"Distance: {distance} cm")

            if distance < 20:
                print("Obstacle detected! Stopping motors.")
                movement_controller.stop()
            else:
                # Track object and adjust movement
                print("Tracking object...")
                frame_centered = object_tracker.track_object()

                if frame_centered:
                    print("Object centered. Moving forward.")
                    movement_controller.move_forward(50)  # Move forward at 50% speed
                else:
                    print("Object not centered. Adjusting position.")
                    
                    # Get the current pan-tilt angles
                    pan_angle = object_tracker.pan_tilt.get_pan_angle()

                    # Adjust robot's direction based on pan angle
                    if pan_angle > 10:  # Object is to the right
                        print("Object is to the right. Turning right.")
                        movement_controller.turn_right(30)  # Turn right at 30% speed
                    elif pan_angle < -10:  # Object is to the left
                        print("Object is to the left. Turning left.")
                        movement_controller.turn_left(30)  # Turn left at 30% speed
                    else:
                        print("Object is roughly centered. Stopping to adjust pan-tilt.")
                        movement_controller.stop()

            time.sleep(0.1)  # Small delay to avoid overwhelming the system

    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        # Cleanup all components
        ultrasonic_sensor.cleanup()
        movement_controller.cleanup()
        print("System cleanup complete.")

if __name__ == "__main__":
    main()