from .base import BaseDriver


class EyeDisplayDriver(BaseDriver):
    """Driver shim for eye displays (ESP32-S3 driven 1.28" panels).

    Provides a compatibility layer for older LedRing driver usage while exposing
    an eye/display oriented self-test.
    """

    name = "eyedisplay"

    def self_test(self):
        # Support both legacy `config.leds` and newer `config.eye` structures.
        cfg = getattr(self, "config", None)
        eye_cfg = None
        if cfg is None:
            return {"name": self.name, "status": "fail", "detail": "no config available"}

        if hasattr(cfg, "eye"):
            eye_cfg = cfg.eye
        elif hasattr(cfg, "leds"):
            eye_cfg = cfg.leds

        if eye_cfg is None:
            return {"name": self.name, "status": "fail", "detail": "no eye/led config found"}

        leds_per_eye = getattr(eye_cfg, "leds_per_eye", getattr(eye_cfg, "pixels_per_eye", None))
        brightness = getattr(eye_cfg, "brightness", 1.0)
        gpio = getattr(eye_cfg, "gpio_pin", "n/a")

        ok = True
        if leds_per_eye is not None:
            ok = leds_per_eye > 0 and 0 <= brightness <= 1

        return {"name": self.name, "status": "pass" if ok else "fail", "detail": f"pin {gpio}, {leds_per_eye} per eye"}


# Backwards-compatible alias for existing imports
LedRingDriver = EyeDisplayDriver
