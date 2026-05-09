"""Drive L298N motor A on ESP32 (MicroPython): ENA = PWM speed, IN1/IN2 = direction.

Wiring (motor A):
  ENA → PWM-capable GPIO (remove the ENA jumper on the module if present)
  IN1, IN2 → GPIO outputs
  Motor A terminals → your DC motor

Change IN1_PIN, IN2_PIN, ENA_PIN below if your wiring differs.
"""

# https://youtu.be/Z0B-FhelaJ8?si=GF4MF5asORFvnBm7

from machine import Pin, PWM
import time

# Motor A — adjust to match your board
IN1_PIN = 0
IN2_PIN = 4
ENA_PIN = 27

PWM_FREQ_HZ = 1000


class MotorA:
    def __init__(self) -> None:
        self._in1 = Pin(IN1_PIN, Pin.OUT, value=0)
        self._in2 = Pin(IN2_PIN, Pin.OUT, value=0)
        self._ena = PWM(Pin(ENA_PIN), freq=PWM_FREQ_HZ, duty_u16=0)

    def stop(self) -> None:
        self._in1.off()
        self._in2.off()
        self._ena.duty_u16(0)

    def forward(self, speed_u16: int = 0xFFFF) -> None:
        """IN1 high, IN2 low (swap in1/in2 if your motor runs the wrong way)."""
        speed_u16 = max(0, min(65535, speed_u16))
        self._in1.on()
        self._in2.off()
        self._ena.duty_u16(speed_u16)

    def reverse(self, speed_u16: int = 0xFFFF) -> None:
        self._in1.off()
        self._in2.on()
        self._ena.duty_u16(speed_u16)

    def deinit(self) -> None:
        self.stop()
        self._ena.deinit()


def main() -> None:
    m = MotorA()
    try:
        # Ramp forward ~75% for 2 s, coast, reverse, stop
        duty = int(0.75 * 65535)
        m.forward(duty)
        time.sleep(2)
        m.stop()
        time.sleep_ms(500)
        m.reverse(duty)
        time.sleep(2)
        m.stop()
    finally:
        m.deinit()


if __name__ == "__main__":
    main()
