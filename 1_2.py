from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import math
import framebuf
import time
from random import randint

button_1 = Pin(9, Pin.IN, Pin.PULL_UP)
button_2 = Pin(8, Pin.IN, Pin.PULL_UP)
button_3 = Pin(7, Pin.IN, Pin.PULL_UP)
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)


class messager:
    def __init__(self):
        self.saved_message = ""
        self.font_size = 8
        self.counter = 0
        self.counter_limit = oled_height // self.font_size
        self.state = self.print_message
        
    def get_message(self):
        self.saved_message = input("Please input your message: ")
        self.state = self.print_message
    
    def print_message(self):
        if self.counter < self.counter_limit:
            oled.text(self.saved_message, 0, 0, 1)
            oled.show()
            oled.scroll(0, self.font_size)
            oled.rect(0, 0, oled.width, self.font_size, 0, True)
            self.counter += 1
        else:
            oled.scroll(0, 0 - self.font_size)
            oled.rect(0, oled_height - self.font_size, oled.width, self.font_size, 0, True)
            oled.text(self.saved_message, 0, oled_height - self.font_size, 1)
            oled.show()
        self.state = self.get_message
    
    def execute(self):
        self.state()

if __name__ == '__main__':
    messenger = messager()
    while True:
        messenger.execute()