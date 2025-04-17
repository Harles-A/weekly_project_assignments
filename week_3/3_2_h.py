from machine import Pin, I2C
import time
from fifo import Fifo
from ssd1306 import SSD1306_I2C

# Constant for the button press event
BUTTON_PRESS = 0

class Encoder:
    def __init__(self, rot_a_pin, rot_b_pin, btn_pin):
        self.a = Pin(rot_a_pin, mode=Pin.IN, pull=Pin.PULL_UP)
        self.b = Pin(rot_b_pin, mode=Pin.IN, pull=Pin.PULL_UP)
        self.button = Pin(btn_pin, mode=Pin.IN, pull=Pin.PULL_UP)
        self.fifo = Fifo(30, typecode='i') 
        self.last_button_time = 0

        self.a.irq(handler=self.rot_handler, trigger=Pin.IRQ_RISING, hard=True)
        self.button.irq(handler=self.btn_handler, trigger=Pin.IRQ_FALLING, hard=True)

    def rot_handler(self, pin):
        if self.b():
            self.fifo.put(-1)
        else:
            self.fifo.put(1)

    def btn_handler(self, pin):
        current = time.ticks_ms()
        # If the button press is within 150 ms of the previous one, ignore it.
        if time.ticks_diff(current, self.last_button_time) < 150:
            return
        self.last_button_time = current
        self.fifo.put(BUTTON_PRESS)

OLED_WIDTH = 128
OLED_HEIGHT = 64

i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c)

menu_items = ["LED1", "LED2", "LED3"]
led_states = [False, False, False]

led_pins = [Pin(22, mode=Pin.OUT), Pin(21, mode=Pin.OUT), Pin(20, mode=Pin.OUT)]
# Turn all LEDs off at the beginning
for pin in led_pins:
    pin.value(0)
    
encoder = Encoder(rot_a_pin=10, rot_b_pin=11, btn_pin=12)

# Current menu selection (index in menu_items list)
selection = 0


def update_menu():
    oled.fill(0)  # clear display
    for i, item in enumerate(menu_items):
        prefix = ">" if i == selection else " "
        state_str = "ON" if led_states[i] else "OFF"
        oled.text("{} {} - {}".format(prefix, item, state_str), 0, i * 16, 1)
    oled.show()

update_menu()

while True:
    if encoder.fifo.has_data():
        event = encoder.fifo.get()
        if event == BUTTON_PRESS:
            led_states[selection] = not led_states[selection]
            led_pins[selection].value(1 if led_states[selection] else 0)
            update_menu()
        elif event == 1:
            selection = (selection + 1) % len(menu_items)
            update_menu()
        elif event == -1:
            selection = (selection - 1) % len(menu_items)
            update_menu()
    time.sleep(0.01)
