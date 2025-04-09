import RPi.GPIO as io
import os
import time

io.setmode(io.BCM)

in1_pin = 16
in2_pin = 18

io.setup(in1_pin, io.OUT)
io.setup(in2_pin, io.OUT)

pwm = io.PWM(in1_pin, 500)  # Set up PWM on in1_pin with 500Hz frequency
pwm.start(0)  # Start PWM with 0% duty cycle

def set_duty_cycle(duty):
    pwm.ChangeDutyCycle(duty)

def clockwise():
    io.output(in1_pin, True)    
    io.output(in2_pin, False)

def counter_clockwise():
    io.output(in1_pin, False)
    io.output(in2_pin, True)

clockwise()

print("Testing clockwise rotation...")
io.output(in1_pin, True)
io.output(in2_pin, False)
time.sleep(2)

print("Testing counter-clockwise rotation...")
io.output(in1_pin, False)
io.output(in2_pin, True)
time.sleep(2)

print("Stopping motor...")
io.output(in1_pin, False)
io.output(in2_pin, False)
io.cleanup()

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
        set_duty_cycle(speed)
    except ValueError:
        print("Invalid speed. Use a number between 0 and 9.")