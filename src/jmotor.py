import RPi.GPIO as io
import os

io.setmode(io.BCM)

in1_pin = 12
in2_pin = 18

io.setup(in1_pin, io.OUT)
io.setup(in2_pin, io.OUT)

def set(property, value):
    try:
        path = f"/sys/class/rpi-pwm/pwm0/{property}"
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return
        with open(path, 'w') as f:
            f.write(value)
    except Exception as e:
        print(f"Error writing to: {property} value: {value}. Exception: {e}")

set("delayed", "0")
set("mode", "pwm")
set("frequency", "500")
set("active", "1")

def clockwise():
    io.output(in1_pin, True)    
    io.output(in2_pin, False)

def counter_clockwise():
    io.output(in1_pin, False)
    io.output(in2_pin, True)

clockwise()

while True:
    cmd = input("Command, f/r 0..9, E.g. f5 :")
    if len(cmd) < 2:
        print("Invalid command. Use format f5 or r3.")
        continue
    direction = cmd[0]
    if direction == "f":
        clockwise()
    elif direction == "r":
        counter_clockwise()
    else:
        print("Invalid direction. Use 'f' for forward or 'r' for reverse.")
        continue
    try:
        speed = int(cmd[1]) * 11
        set("duty", str(speed))
    except ValueError:
        print("Invalid speed. Use a number between 0 and 9.")