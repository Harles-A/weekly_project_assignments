from machine import Pin, PWM
import time
from fifo import Fifo

class Encoder:
    def __init__(self, rot_a, rot_b):
        self.a = Pin(rot_a, mode=Pin.IN, pull=Pin.PULL_UP)
        self.b = Pin(rot_b, mode=Pin.IN, pull=Pin.PULL_UP)
        self.fifo = Fifo(30, typecode='i')
        self.a.irq(handler=self.handler, trigger=Pin.IRQ_RISING, hard=True)

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

class Switch(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.down = False

    def pressed(self):
        if self.down:
            if not super().pressed():
                self.down = False
        else:
            if super().pressed():
                self.down = True
                return True
        return False

rot = Encoder(10, 11)
button = Switch(12, Pin.IN, Pin.PULL_UP)
led_pwm = PWM(Pin(21))
led_pwm.freq(1000)

led_on = False
brightness = 512 

print("Program started. LED is off. Initial brightness =", brightness)

while True:
    time.sleep(0.005) 

    if button.pressed():
        led_on = not led_on
        if led_on:
            led_pwm.duty_u16(brightness * 64) 
            print("LED turned ON. Current brightness =", brightness)
        else:
            led_pwm.duty_u16(0)
            print("LED turned OFF.")

    if led_on:
        while rot.fifo.has_data():
            turn = rot.fifo.get()
            brightness += turn * 20
            brightness = min(max(brightness, 0), 1023)
            led_pwm.duty_u16(brightness * 64)
            print("Encoder turn:", turn, "Adjusted brightness to:", brightness)
    else:
        # Clear out any encoder events from the FIFO so they aren't applied later
        while rot.fifo.has_data():
            _ = rot.fifo.get()  # Discards turns while LED is off

