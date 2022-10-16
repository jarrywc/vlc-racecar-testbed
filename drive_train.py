from pyvesc import VESC
from queue import Queue
import subprocess
import serial
import math
import time
import csv

# Global Values

nav_queue = Queue()

STATIC_DIMENSIONS = {
    'WIDTH_FRONT_AXLE': 5,
    'RADIUS_AXLE_TO_FRONT_WHEEL': 1,
    'LENGTH_BTW_FRONT_REAR_AXLES': 20
}

CALIBRATED_METER = 4.57
CALIBRATED_SEC = 5

WHEEL_RADIUS = .055

DURATION_PRECISION = 100  # 1 / Frequency (Hz)

MOTOR_HEARTBEAT = False
# Turn Values that modulate the turn angle for hardware,
# these vary by servo hardware position
SERVO_MAX = .889
SERVO_MIN = .117
SERVO_CENTER = .565  # this is the center, zero value 
# Degrees range values to proportion with the servo values
LEFT_MAX = -30  # this is degrees value from center toward left (counter-clock-wise)
RIGHT_MAX = 30  # this is degrees value from center toward right (clock-wise)
# Latter methods will function to translate user degree value input to become
# --- an accurate servo value

# Duty Cycle Standard Values
DUTY_MAX = .2
DUTY_MIN = .05  # Minimum Value to Move: turn motor, car wheels spin & car moves

# Drive Train is controlled via Vesc Object ( Need to add INIT error handling )
# serial port that VESC is connected to. Something like "COM3" for windows and as below for linux/mac
drivetrain = VESC(serial_port='/dev/serial/by-id/usb-STMicroelectronics_ChibiOS_RT_Virtual_COM_Port_304-if00')


# Input: Servo Value | Output: Physical Hardware Motor Control
def set_servo(servo_value):
    global drivetrain, SERVO_CENTER
    drivetrain.servo(servo_value)
    if servo_value == SERVO_CENTER:
        drivetrain.stop_heartbeat()


# Input: Turn value as degrees, negative is left & positive is right
# Output: Turn value as servo value, range is proportional to angle
def turn_angle(turn_degrees):
    if 0 < turn_degrees <= RIGHT_MAX:
        # Math: Servo (max - ctr) is the total servo steps for right turn
        # servo steps / right max is the qty of steps per degree
        # turn degrees * ( servo steps per degree / right max ) is the current servo steps translation
        set_servo(turn_degrees * (SERVO_MAX - SERVO_CENTER) / RIGHT_MAX)
    elif 0 > turn_degrees >= LEFT_MAX:
        # Follow similar math, leave both negatives (they become positive),
        # and index from higher servo value for range (aka abs val)
        set_servo(turn_degrees * (SERVO_CENTER - SERVO_MIN) / LEFT_MAX)
    else:
        set_servo(SERVO_CENTER)  # Go to the middle value


def speed_to_rpm(speed):
    w = speed / WHEEL_RADIUS
    print('Angular Velocity', w)
    rpm = (60 * w) / (2 * math.pi)
    print('RPM ', rpm)
    return rpm


def speed_to_duty(speed):
    global DUTY_MAX, CALIBRATED_METER, CALIBRATED_SEC
    duty = speed * (DUTY_MAX/ (CALIBRATED_METER/CALIBRATED_SEC))
    print('Duty', duty)
    return duty


# Input: Duty cycle value as %
# Output: Car movement via drivetrain object
def move_motor_duty(duty_cycle):
    global drivetrain
    print(duty_cycle)
    drivetrain.SetDutyCycle(duty_cycle)


# Input: Linear velocity
# Output: Car movement via drivetrain object
def move_motor(speed):
    global drivetrain
    print('Speed ', speed)
    # rpm = int(speed_to_rpm(speed))
    # drivetrain.set_rpm(rpm)
    duty = speed_to_duty(speed)
    drivetrain.set_duty_cycle(duty)


# Input:

# Input: Velocity in m/s
# Output: Car movement over duration in seconds
def move_vehicle(speed, duration):
    global DURATION_PRECISION, drivetrain, MOTOR_HEARTBEAT
    counter = 0
    while counter < duration :
        if not MOTOR_HEARTBEAT:
            MOTOR_HEARTBEAT = True
        # move_motor(speed)
        move_motor(speed)
        time.sleep(duration / DURATION_PRECISION)
        counter += 1
    drivetrain.stop_heartbeat()
    MOTOR_HEARTBEAT = False


def move_vehicle_q(step=list):
    move_vehicle(step[0], step[1])


def drive_route_csv(navigation_file):
    with open(navigation_file) as nav_file:
        read_nav_file = csv.reader(nav_file)
        for row in read_nav_file:
            if row is not 1:
                move_vehicle(float(row[0]), float(row[1]))


def add_step_to_queue(step=list):
    global nav_queue
    nav_queue.put(step)


def drive_route_queue():
    global nav_queue
    while not nav_queue.empty():
        movenav_queue.get()


def main():
    global drivetrain
    while True:
        try:
            print('Enter speed: ')
            speed = float(input())
            print('Enter duration: ')
            duration = float(input())
            move_vehicle(speed, duration)
        except KeyboardInterrupt:
            drivetrain.stop_heartbeat()
            exit()


def main1():
    global drivetrain
    drive_route_csv('test.csv')

if __name__ == "__main__":
    main()
