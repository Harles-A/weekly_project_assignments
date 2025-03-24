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


class ufo:
    def __init__(self):
        self.ufo = '<=>'
        self.size = 11
        self.x = oled_width // 2
        self.y = oled.height
        self.x_min = 0 + self.size
        self.x_max = oled.width - self.size
        self.state = self.draw
    
    def move(self, direction):
        if self.x > self.x_min and self.x < self.x_max:
            self.x += 1 * direction
        elif self.x == self.x_min:
            self.x += 1
        elif self.x == self.x_max:
            self.x -= 1
            
    def listen(self):
        if button_1() == 0:
            self.move(1)
            self.state = self.draw
        elif button_3() == 0:
            self.move(-1)
            self.state = self.draw
            
            
    def draw(self):
        oled.fill(0)
        oled.text(self.ufo, self.x - self.size, self.y - self.size, 1)
        oled.show()
        self.state = self.listen
    
    def execute(self):
        self.state()
    
if __name__ == '__main__':
    test = ufo()
    while True:
            test.execute()