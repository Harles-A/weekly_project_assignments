from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from fifo import Fifo
from led import Led
import micropython
import framebuf
import time


micropython.alloc_emergency_exception_buf(200)

position = 0
INTERRUPTION_DELAY = 150

class Screen:
    def __init__(self):
        self.i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
        self.oled_width = 128
        self.oled_height = 64
        self.oled = SSD1306_I2C(self.oled_width, self.oled_height, self.i2c)
        self.items = ["LED 1", "LED 2", "LED 3"]
        self.text_size = 8
        self.direction = 1
    
    def draw(self):
        global position
        self.oled.fill(0)
        for i in range(len(self.items)):
            self.oled.text(self.items[i], 0, (i * self.text_size), 1)
            if position == i:
                self.oled.fill_rect(0,
                               (i * self.text_size),
                               (len(self.items[i]) * self.text_size),
                               (self.text_size),
                               1)
                self.oled.text(self.items[i], 0, (i * self.text_size), 0)
        self.oled.show()
    
    def change_location(self):
        global position
        if position == 0 and self.direction == -1:
            self.direction += 2
        elif abs(position // (len(self.items) - 1)) == 1 and position > 0:
            self.direction -= 2
        position += self.direction



class Encoder:
    def __init__(self, a, b, c, led_0, led_1, led_2):
        self.a = Pin(a, Pin.IN)
        self.b = Pin(b, Pin.IN)
        self.c = Pin(c, Pin.IN, Pin.PULL_UP)
        self.led_list = [led_0, led_1, led_2]
        self.led_status = {"led_0":"off", "led_1":"off", "led_2":"off"}
        self.fifo = Fifo(30)
        self.a.irq(self.handler, Pin.IRQ_RISING, hard = True)
        self.c.irq(self.button_handler, Pin.IRQ_RISING, hard = True)
        self.time_interrupted = 0
        
    def led_control(self):
        if self.led_status[f"led_{position}"] == "off":
            Led(self.led_list[position]).on()
            self.led_status[f"led_{position}"] = "on"
        else:
            Led(self.led_list[position]).off()
            self.led_status[f"led_{position}"] = "off"
            
    def handler(self, pin):
        current_time = time.ticks_ms()
        if (time.ticks_diff(current_time, self.time_interrupted) > INTERRUPTION_DELAY):
            self.time_interrupted = current_time
            if self.a():
                self.fifo.put(1)
    
    def button_handler(self, pin):
        current_time = time.ticks_ms()
        if (time.ticks_diff(current_time, self.time_interrupted) > INTERRUPTION_DELAY):    
            self.fifo.put(0)
        self.time_interrupted = current_time
        

if __name__ == '__main__':
    rot = Encoder(10, 11, 12, 22, 21, 20)
    screen = Screen()
    screen.draw()
    
    
    while True:
        if rot.fifo.has_data():
            input = rot.fifo.get()
            if input == 1:
                screen.change_location()
            else:
                rot.led_control()
        screen.draw()