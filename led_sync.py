import time
import busio
import board
import Jetson.GPIO as GPIO
from adafruit_ht16k33 import matrix
i2c = busio.I2C(board.SCL, board.SDA)


# Sets LEDs as a list, reducing recalculation overhead for each bit transmitted
def activate_leds(frame):
    active_led_list = []
    if frame > 0:
        min_frame = frame - 1  # If frame = 2 then min_f = 1
        max_frame = 8 - frame
        for i in range(0, 8):
            for j in range(0, 8):
                # Add the active LEDs that will be frame only
                if not min_frame < i < max_frame or not min_frame < j < max_frame:
                    print("{}, {}".format(i, j))
                    current = i, j
                    active_led_list.append(current)
        return active_led_list
    else:
        for i in range(0, 7):
            for j in range(0, 7):
                active_led_list.append(matrix[i, j])
        return active_led_list


class LED_S():
    def __init__(self, address1, address2, frame):
        self.left = matrix.Matrix8x8(i2c, address1)
        self.right = matrix.Matrix8x8(i2c, address2)
        self.active = activate_leds(frame)
        self.center = GPIO
        self.output_pin = "SOC_GPIO54" # TEGRA_SOC Mode / 22-BCM / 15-BOARD
        self.center.setup(self.output_pin, GPIO.OUT, initial=GPIO.LOW)
    def high(self, matrix):
        for i in range(1, 9):
            for j in range(1, 9):
                if i % 2 or j % 2 == 0:
                    pass
                else:
                    matrix[i, j] = 1
                    matrix.show()
    def low(self, matrix):
        for i in range(1, 9):
            for j in range(1, 9):
                if i % 2 or j % 2 == 0:
                    pass
                else:
                    matrix[i, j] = 0
                    matrix.show()
    def high_frame(self):
        for led in self.active:
            self.left[led] = 1
            self.right[led] = 1
    def high_all(self):
        self.left.fill(1)
        self.right.fill(1)
    def low_all(self):
        self.left.fill(0)
        self.right.fill(0)
    def transfer_bit(self, bit, counter):
        # print(counter) # self.center.output(output_pin, int(bit))
        if int(bit) == 1:
            self.high_all()
            self.center.output(self.output_pin, self.center.HIGH)
            print(1)
        else:
            self.low_all()
            self.center.output(self.output_pin, self.center.LOW)
    def cleanup(self):
        self.low_all()
        self.center.output(self.output_pin, self.center.LOW)
        self.center.cleanup(output_pin)
# matrix = LED_S(0x70, 0x73, 1)

