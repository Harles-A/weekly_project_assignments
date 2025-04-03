import time
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

oled_width = 128
oled_height = 64
font_height = 8

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(oled_width, oled_height, i2c)

max_lines = oled_height // font_height 

lines = []

while True:
    user_input = input("Enter text: ")
    
    if len(lines) >= max_lines:
        lines.pop(0)
    
    lines.append(user_input)
    
    oled.fill(0)
    
    for index, text in enumerate(lines):
        y = index * font_height
        oled.text(text, 0, y, 1)
    
    oled.show()
    
    time.sleep(0.05)
