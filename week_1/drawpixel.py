import time
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

oled_width = 128
oled_height = 64

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(oled_width, oled_height, i2c)

sw2 = Pin(7, Pin.IN, Pin.PULL_UP)
sw1 = Pin(8, Pin.IN, Pin.PULL_UP)
sw0 = Pin(9, Pin.IN, Pin.PULL_UP)

x = 0
y = oled_height // 2

x_step = 1
delay = 0.05

while True:
    if sw1.value() == 0:
        oled.fill(0)
        x = 0
        y = oled_height // 2
        while sw1.value() == 0:
            time.sleep(0.01)
    
    if sw2.value() == 0:
        y = max(0, y - 1)
        time.sleep(0.01)
    
    if sw0.value() == 0:
        y = min(oled_height - 1, y + 1)
        time.sleep(0.01)
    
    oled.pixel(x, y, 1)
    oled.show()
    
    x += x_step
    if x >= oled_width:
        x = 0

    time.sleep(delay)
