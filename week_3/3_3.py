from machine import Pin, I2C
from filefifo import Filefifo
from fifo import Fifo
from ssd1306 import SSD1306_I2C
import time

class Encoder:
    def __init__(self, rot_a, rot_b):
        self.a = Pin(rot_a, mode = Pin.IN)
        self.b = Pin(rot_b, mode = Pin.IN)
        self.fifo = Fifo(30, typecode = "i")
        self.a.irq(handler = self.handler, trigger = Pin.IRQ_RISING, hard = True)
        
    def handler(self, pin):
        if self.b():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)

# initialize encoder
rot = Encoder(10, 11)

# initialize oled
OLED_WIDTH = 128
OLED_HEIGHT = 64
i2c = I2C(1, scl = Pin(15), sda = Pin(14), freq = 400000)
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)

# get the data
sample_size = 1000 # maximum
source_file = 'capture_250Hz_01.txt'
source_fifo = Filefifo(100, name = source_file)
data = [source_fifo.get() for _ in range(sample_size)]

max_val = max(data)
min_val = min(data)

# scale the values against oled height (64 - 1)
scale_num = (OLED_HEIGHT - 1) / (max_val - min_val)

for i in range(len(data) - 1):
    data[i] = int((data[i] - min_val) * scale_num)
 
# track index for calculating correct x-pos in oled
idx = 0

# main program
while True:
    while rot.fifo.has_data():
        idx += rot.fifo.get()        
        idx = max(0, min(idx, len(data) - OLED_WIDTH))

    oled.fill(0)
    #print(idx)
    
    for i in range(OLED_WIDTH):
        oled.pixel(i, data[idx + i], 1)
        
    oled.show()