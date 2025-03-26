from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import math
import framebuf
import time
from random import randint

sw0 = Pin(9, Pin.IN, Pin.PULL_UP)
sw1 = Pin(8, Pin.IN, Pin.PULL_UP)
sw2 = Pin(7, Pin.IN, Pin.PULL_UP)
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)


class liner:
    def __init__(self):
        self.x_start = 0
        self.y_start = oled_height // 2
        self.x = self.x_start
        self.y = self.y_start
        self.wait = time.sleep(0.02)
        self.state = self.draw_dot
        
    def move(self, direction):
        self.y += direction
        
    def draw_dot(self):
        self.x += 1
        if self.x < oled_width:
            oled.pixel(self.x, self.y, 1)
            oled.show()
        else:
            self.x = 0
            oled.pixel(self.x, self.y, 1)
            oled.show()
        self.state = self.listen
        
    def listen(self):
        if sw2() == 0:
            if self.y < oled_height:
                self.move(1)
            
        elif sw0() == 0:
            if self.y > 0:
                self.move(-1)
            
        elif sw1() == 0:
            oled.fill(0)
            oled.show()
            self.x = self.x_start
            self.y = self.y_start
        
        self.state = self.draw_dot
    
    def execute(self):
        self.state()
        
if __name__ == '__main__':
    worm = liner()
    while True:
        worm.execute()