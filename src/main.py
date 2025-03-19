import threading
import signal
from servo_control import ServoControl
from ultrasonic_sensor import UltrasonicSensor
from boundary_detection import QTRSensorThread 

def main():
    stop_event = threading.Event()

    servo_control = ServoControl(stop_event)
    ultrasonic_sensor = UltrasonicSensor(stop_event)
    qtr_sensor= QTRSensorThread(stop_event)

    servo_thread = threading.Thread(target=servo_control.run)
    ultrasonic_thread = threading.Thread(target=ultrasonic_sensor.run)
    qtr_thread = threading.Thread(target=qtr_sensor.run)  # <-- Add QTR thread
    def signal_handler(sig, frame):
        print("KeyboardInterrupt received, stopping threads...")
        stop_event.set()
        servo_thread.join()
        ultrasonic_thread.join()
        qtr_thread.join()
        print("Threads stopped, exiting program.")

    signal.signal(signal.SIGINT, signal_handler)

    servo_thread.start()
    ultrasonic_thread.start()
    qtr_thread.start()

    servo_thread.join()
    ultrasonic_thread.join()
    qtr_thread.join()
if __name__ == "__main__":
    main()