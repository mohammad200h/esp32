"""Drive a hobby servo on GPIO 23 (MicroPython on ESP32, 50 Hz PWM)."""
from machine import Pin, PWM
import time

# Standard servo: ~1 ms (0°) to ~2 ms (180°) pulse in a 20 ms frame at 50 Hz.
SERVO_FREQ_HZ = 50
FRAME_US = 1_000_000 // SERVO_FREQ_HZ  # 20_000 µs


def _clamp_angle(angle_deg: float) -> float:
    angle_deg = max(0.0, min(180.0, angle_deg))
    return angle_deg


def angle_to_duty_u16(angle_deg: float) -> int:
    angle_deg = _clamp_angle(angle_deg)
    pulse_us = 1000 + (angle_deg / 180.0) * 1000
    return int((pulse_us / FRAME_US) * 65535)


class Servo:
    def __init__(self, pin: int = 23, initial_angle: float = 90.0) -> None:
        self.pwm = PWM(Pin(pin), freq=SERVO_FREQ_HZ)
        self.angle = 0.0
        self.set_angle(initial_angle)

    def set_angle(self, angle_deg: float) -> None:
        self.angle = _clamp_angle(angle_deg)
        self.pwm.duty_u16(angle_to_duty_u16(self.angle))

    def deinit(self) -> None:
        self.pwm.deinit()


def main() -> None:
    servo = Servo(23, initial_angle=0)
    try:
        while True:
            for a in range(0, 181, 2):
                servo.set_angle(a)
                time.sleep_ms(15)
            for a in range(180, -1, -2):
                servo.set_angle(a)
                time.sleep_ms(15)
    finally:
        servo.deinit()


if __name__ == "__main__":
    main()
