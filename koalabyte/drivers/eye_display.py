from .base import BaseDriver


class EyeDisplayDriver(BaseDriver):
    """Driver shim for the EYE1 ESP32-S3 dual round LCD eye board."""

    name = "eye_display"

    def self_test(self):
        eyes = getattr(self.config, "eyes", None)
        eye_display = getattr(self.config, "eye_display", None)
        if eyes is None or eye_display is None:
            return {"name": self.name, "status": "fail", "detail": "missing eyes/eye_display config"}

        if getattr(eyes, "ref", None) != "EYE1":
            return {"name": self.name, "status": "fail", "detail": "eyes ref must be EYE1"}
        if getattr(eye_display, "board_ref", None) != "EYE1":
            return {"name": self.name, "status": "fail", "detail": "eye_display board_ref must be EYE1"}
        if getattr(eye_display, "legacy_ws2812_eye_rings", True):
            return {"name": self.name, "status": "fail", "detail": "legacy WS2812 eye rings must be disabled"}

        board = getattr(eyes, "controller", "unknown dual-eye board")
        interface = getattr(eyes, "interface", "unknown interface")
        detail = f"EYE1 {board} via {interface}; no LED_L/LED_R WS2812 ring driver"
        return {"name": self.name, "status": "pass", "detail": detail}

    def initialize(self):
        eyes = self.config.eyes
        return f"{self.name}: {eyes.ref} {eyes.controller} initialized over {eyes.interface}"
