"""HC-SR04 ultrasonic distance sensor on ESP32 (MicroPython).

Wiring:
  VCC  -> 5V (the module needs 5V to fire properly)
  GND  -> GND
  TRIG -> any output-capable GPIO (e.g. 5)
  ECHO -> input GPIO via a 5V->3.3V divider (e.g. 1k / 2k)
          input-only pins like 34/35 are OK for ECHO.

Note: On ESP32, GPIO 34/35/36/39 are INPUT ONLY, so TRIG cannot live there.
"""

# https://www.youtube.com/watch?v=n-gJ00GTsNg

from machine import Pin, time_pulse_us
import time

ECHO = 34   # input-only pin is fine for ECHO
TRIG = 32    # must be output-capable (NOT 34/35/36/39)

# Speed of sound ~343 m/s = 0.0343 cm/µs. Round-trip, so divide by 2.
US_PER_CM = 2.0 / 0.0343  # ≈ 58.31 µs per cm

# HC-SR04 holds ECHO high for up to ~38 ms when no object; match that so we
# don't clip a slow edge. Slightly over is fine for close-range use.
ECHO_TIMEOUT_US = 40_000


class UltrasonicSensor:
    def __init__(self, trig_pin: int = TRIG, echo_pin: int = ECHO) -> None:
        self._trig = Pin(trig_pin, Pin.OUT, value=0)
        self._echo = Pin(echo_pin, Pin.IN)
        # Let the module settle after power-up.
        time.sleep_ms(50)

    def _pulse_us(self) -> int:
        """Fire a 10 µs trigger and return echo high-time in µs (-1/-2 on timeout)."""
        self._trig.off()
        time.sleep_us(2)
        self._trig.on()
        time.sleep_us(10)
        self._trig.off()
        return time_pulse_us(self._echo, 1, ECHO_TIMEOUT_US)

    def distance_cm(self, retries: int = 3) -> float:
        """Return distance in cm, or -1.0 if no echo was received after retries."""
        for attempt in range(retries):
            dt = self._pulse_us()
            if dt >= 0:
                return dt / US_PER_CM
            # Occasional misses are normal (acoustics, noise on ECHO); wait before re-ping.
            time.sleep_ms(5)
        return -1.0

    def distance_cm_avg(self, samples: int = 5, gap_ms: int = 30) -> float:
        """Median-of-N reading to reject the occasional bad ping."""
        readings = []
        for _ in range(samples):
            d = self.distance_cm()
            if d >= 0:
                readings.append(d)
            time.sleep_ms(gap_ms)
        if not readings:
            return -1.0
        readings.sort()
        return readings[len(readings) // 2]


def main() -> None:
    sensor = UltrasonicSensor()
    while True:
        d = sensor.distance_cm()
        if d < 0:
            print("out of range")
        else:
            print("{:6.1f} cm".format(d))
        # HC-SR04 datasheet: keep >=60 ms between triggers to avoid echoes overlapping.
        time.sleep_ms(80)


if __name__ == "__main__":
    main()
