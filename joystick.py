from machine import ADC, Pin
import time

# Connections (example — adjust GPIOs if you wire differently):
# Joystick VCC -> 3V3  (use 3.3 V so ADC range matches; do not use 5 V on ADC pins)
# Joystick GND -> GND
# Joystick VERT -> GPIO32 (ADC1_CH4)
# Joystick HORZ -> GPIO35 (ADC7)
# Joystick SEL  -> GPIO21 (digital; module ties to GND when pressed — use pull-up)

VERT_PIN = 32
HORZ_PIN = 35
SEL_PIN = 21

# Quieter readings when the stick is still: ESP32 ADC + pot noise jitters a few counts.
AVG_SAMPLES = 16
# 0.2–0.4: smoother when idle; higher = follows the pot faster. None = averaging only.
EMA_ALPHA = 0.28


class AnalogJoystick:
    """Reads a 2-axis analog joystick + push-button (SEL)."""

    def __init__(
        self,
        vert_pin: int,
        horz_pin: int,
        sel_pin: int,
        *,
        avg_samples: int = AVG_SAMPLES,
        ema_alpha=EMA_ALPHA,
    ):
        self._vert = ADC(Pin(vert_pin))
        self._horz = ADC(Pin(horz_pin))
        # Full-scale ~3.3 V on ESP32 ADC (required for 0–3.3 V joystick output)
        self._vert.atten(ADC.ATTN_11DB)
        self._horz.atten(ADC.ATTN_11DB)
        self._sel = Pin(sel_pin, Pin.IN, Pin.PULL_UP)
        self._avg_samples = max(1, int(avg_samples))
        self._ema_alpha = ema_alpha
        self._ema_v = None
        self._ema_h = None

    def _avg_read(self, adc: ADC) -> int:
        s = 0
        for _ in range(self._avg_samples):
            s += adc.read()
        return s // self._avg_samples

    def _smooth(self, value: int, prev):
        if self._ema_alpha is None:
            return value, float(value)
        if prev is None:
            return value, float(value)
        n = prev * (1.0 - self._ema_alpha) + float(value) * self._ema_alpha
        return int(round(n)), n

    def raw_vert(self) -> int:
        avg = self._avg_read(self._vert)
        out, self._ema_v = self._smooth(avg, self._ema_v)
        return out

    def raw_horz(self) -> int:
        avg = self._avg_read(self._horz)
        out, self._ema_h = self._smooth(avg, self._ema_h)
        return out

    def pressed(self) -> bool:
        # Most modules: LOW when the stick is clicked
        return self._sel.value() == 0


def main():
    stick = AnalogJoystick(VERT_PIN, HORZ_PIN, SEL_PIN)
    while True:
        print("VERT:", stick.raw_vert(), "HORZ:", stick.raw_horz(), "SEL:", stick.pressed())
        time.sleep(0.1)


if __name__ == "__main__":
    main()
