"""Blink the LED on GPIO 2 (MicroPython on ESP32)."""
from machine import Pin
import time

led = Pin(2, Pin.OUT)

while True:
    led.on()
    time.sleep_ms(500)
    led.off()
    time.sleep_ms(500)
