from .base import BaseDriver


class LedRingDriver(BaseDriver):
    name = "ledring"

    def self_test(self):
        leds = self.config.leds
        ok = leds.leds_per_eye > 0 and 0 <= leds.brightness <= 1
        return {"name": self.name, "status": "pass" if ok else "fail", "detail": f"pin {leds.gpio_pin}, {leds.leds_per_eye} LEDs per eye"}
