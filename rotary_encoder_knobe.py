from machine import Pin
import time

# Connections:
# SW  -> GPIO16
# DT  -> GPIO17
# CLK -> GPIO5

SW_PIN = 16
DT_PIN = 17
CLK_PIN = 5

class RotaryEncoderKnobe:
    def __init__(self, sw_pin: int, dt_pin: int, clk_pin: int):
        ######## setup pins ########
        # button
        self.sw_pin = Pin(sw_pin, Pin.IN, Pin.PULL_UP)
        # data
        self.dt_pin = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        # clock
        self.clk_pin = Pin(clk_pin, Pin.IN, Pin.PULL_UP)

        ######### setup interrupts ########
        self.sw_pin.irq(trigger=Pin.IRQ_FALLING, handler=self._on_button)
        self.clk_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._on_clk)
        #########State #########
        self._button_pressed = False
        self._last_clk = self.clk_pin.value()
        self.max_value = 100
        self.min_value = 0
        self._value = 0
        self._value_changed = False
    
        

    @property
    def button_pressed(self):
        return self._button_pressed
    @property
    def value_changed(self):
        return self._value_changed

    @property
    def value(self):
        return self._value

    def _on_button(self, _pin):
        self._button_pressed = not self._button_pressed
        

    def _on_clk(self, _pin):
        c = self.clk_pin.value()
        if c == self._last_clk:
            self._value_changed = False
            return
        self._last_clk = c

        if self.dt_pin.value() != c:
            self._value += 1
            self._value_changed = True
        else:
            self._value -= 1
            self._value_changed = True
       

   