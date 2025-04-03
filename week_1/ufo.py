import time
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

oled_width = 128
oled_height = 64

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(oled_width, oled_height, i2c)

sw0 = Pin(9, Pin.IN, Pin.PULL_UP)
sw2 = Pin(7, Pin.IN, Pin.PULL_UP) 

ufo_symbol = "<=>"
ufo_width = 24 
ufo_y = oled_height - 8 
ufo_x = (oled_width - ufo_width) // 2 

step = 8 
min_x = 0
max_x = oled_width - ufo_width

while True:
    if sw0.value() == 0:
        if ufo_x < max_x:
            ufo_x += step
            if ufo_x > max_x:
                ufo_x = max_x
    elif sw2.value() == 0:
        if ufo_x > min_x:
            ufo_x -= step
            if ufo_x < min_x:
                ufo_x = min_x

    oled.fill(0)
    oled.text(ufo_symbol, ufo_x, ufo_y, 1)
    oled.show()

    time.sleep(0.15)
