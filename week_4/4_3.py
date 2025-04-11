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
            
class Button(Pin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.press = 0
        self.release = 0
        self.state = False
        self.down = False

    def pressed(self):
        if self.value() == 0:
            self.release = 0
            self.press += 1
            if self.press >= 3:
                self.press = 3
                self.state = True
        else:
            self.press = 0
            self.release += 1
            if self.release >= 3:
                self.release = 3
                self.state = False
                
        return self.state
    
    def single_press(self):
        if self.down:
            if not self.pressed():
                self.down = False
        else:
            if self.pressed():
                self.down = True
                return True
        return False
    
# helper for getting averaged values from the data
def get_avg_values(filefifo, size):
    buffer = []
    buffer_size = 5 # adjust to change signal size
    count = 0
    
    while count < size:
        try:
            value = filefifo.get()
        except:
            return 0
    
        buffer.append(value)
        count += 1

        if len(buffer) == buffer_size:
            avg = sum(buffer) / buffer_size
            yield avg
            buffer.clear()
    
# initialize encoder, switch and buttons
rot = Encoder(10, 11)
sw_0 = Button(9, Pin.IN, Pin.PULL_UP)
sw_1 = Button(8, Pin.IN, Pin.PULL_UP)
sw_2 = Button(7, Pin.IN, Pin.PULL_UP)

# initialize oled
OLED_WIDTH = 128
OLED_HEIGHT = 64
i2c = I2C(1, scl = Pin(15), sda = Pin(14), freq = 400000)
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)
oled.fill(0) # initial clear

# data variables
SOURCE_FILE = "capture02_250Hz.txt"
SAMPLE_SIZE = 1800

source_fifo = None
data = None
    
# wait for initial sw_1 press to get data
while not source_fifo:
    if sw_1.single_press():
        source_fifo = Filefifo(100, name = SOURCE_FILE)
        print("Source fifo initialized")
    else:
        oled.text("Press SW_1", 24, int(OLED_HEIGHT / 3), 1)
        oled.show()

# get the averaged data
data = tuple(get_avg_values(source_fifo, SAMPLE_SIZE))

# no data => freeze text
while not data:
    oled.text("No data!", 24, int(OLED_HEIGHT / 2), 1)
    oled.show()
    time.sleep(1)

# recalculate the values to fit in oled
min_val = min(data)
max_val = max(data)
scale_num = (OLED_HEIGHT - 1) / (max_val - min_val)

data = tuple(int((data[i] - min_val) * scale_num) for i in range(len(data) - 1))

# the loop below does the same thing as the inline loop above, but for a list updating items
# for i in range(len(data) - 1):
#    data[i] = int((data[i] - min_val) * scale_num)

idx = 0 # track index for calculating correct x-pos in oled
scale_factor = 100 # scale percentage
offset = 0 # y-pos offset

# main program
while True:
    while rot.fifo.has_data():
        delta = rot.fifo.get()

        if sw_2.pressed(): # sw_2 pressed => scale the signal with enc. scroll
            scale_factor += delta
            scale_factor = max(1, min(scale_factor, 1000))
            print(f"Scale {scale_factor}%")
        elif sw_0.pressed(): # sw_0 pressed => move the signal vertically on oled
            offset += delta
            print(f"Current y-offset: {offset}")
        else: # otherwise => scroll the signal as is
            idx += delta
            idx = max(0, min(idx, len(data) - OLED_WIDTH))

    oled.fill(0)

    for i in range(OLED_WIDTH - 2):
        raw_y = data[idx + i]
        
        # apply the scale & offset factors
        y = (raw_y - offset) * scale_factor // 100
        y = max(0, min(y, OLED_HEIGHT - 1))
    
        # calculate the next y point to correctly draw a line
        next_raw_y = data[idx + i + 1]
        next_y = (next_raw_y - offset) * scale_factor // 100
        next_y = max(0, min(next_y, OLED_HEIGHT - 1))

        oled.line(i, y, i + 1, next_y, 1)
    
    oled.show()