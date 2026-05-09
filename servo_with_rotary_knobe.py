from servo import Servo
from rotary_encoder_knobe import RotaryEncoderKnobe

servo = Servo(pin=23, initial_angle=90.0)
knobe = RotaryEncoderKnobe(sw_pin=16, dt_pin=17, clk_pin=5)

while True:
    if knobe.value_changed:
        print(f"Value changed, value: {knobe.value}")
        servo.set_angle(knobe.value)
    # if knobe.button_pressed:
    #     print(f"Button pressed")
    #     servo.set_angle(0)
 
