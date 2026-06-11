from .base import BaseDriver


class EyeDisplayDriver(BaseDriver):
    """Backward-compatible shim for legacy LedRingDriver imports.

    Rev 0.5 no longer uses separate LED_L/LED_R WS2812 rings. Legacy callers may
    still import koalabyte.drivers.ledring.LedRingDriver, so this shim resolves
    the canonical KoalaByteConfig fields (`eyes` and `eye_display`) and reports
    the EYE1 ESP32-S3 dual-LCD eye board state instead of failing on missing
    legacy `eye` / `leds` attributes.
    """

    name = "eyedisplay"

    def _resolve_eye_config(self):
        cfg = getattr(self, "config", None)
        if cfg is None:
            return None, None

        eyes = getattr(cfg, "eyes", None)
        eye_display = getattr(cfg, "eye_display", None)

        # Older compatibility field names retained for external integrations.
        if eyes is None:
            eyes = getattr(cfg, "eye", None)
        if eye_display is None:
            eye_display = getattr(cfg, "leds", None)

        return eyes, eye_display

    def self_test(self):
        eyes, eye_display = self._resolve_eye_config()
        if eyes is None or eye_display is None:
            return {"name": self.name, "status": "fail", "detail": "no eyes/eye_display config found"}

        ref = getattr(eyes, "ref", getattr(eye_display, "board_ref", "unknown"))
        board_ref = getattr(eye_display, "board_ref", ref)
        controller = getattr(eyes, "controller", getattr(eye_display, "board", "unknown eye board"))
        interface = getattr(eyes, "interface", "unknown interface")
        brightness = getattr(eye_display, "brightness", 1.0)
        legacy_rings = getattr(eye_display, "legacy_ws2812_eye_rings", False)

        if ref != "EYE1" or board_ref != "EYE1":
            return {"name": self.name, "status": "fail", "detail": "expected EYE1 dual-eye board config"}
        if legacy_rings:
            return {"name": self.name, "status": "fail", "detail": "legacy WS2812 eye rings are disabled for Rev 0.5"}
        if not 0 <= brightness <= 1:
            return {"name": self.name, "status": "fail", "detail": "eye display brightness must be 0..1"}

        detail = f"EYE1 {controller} via {interface}; no LED_L/LED_R WS2812 ring driver"
        return {"name": self.name, "status": "pass", "detail": detail}

    def initialize(self):
        eyes, _eye_display = self._resolve_eye_config()
        if eyes is None:
            return f"{self.name}: no eyes config available"
        ref = getattr(eyes, "ref", "EYE1")
        controller = getattr(eyes, "controller", "ESP32-S3 dual-eye LCD board")
        interface = getattr(eyes, "interface", "USB/UART")
        return f"{self.name}: {ref} {controller} initialized over {interface}"


# Backwards-compatible alias for existing imports.
LedRingDriver = EyeDisplayDriver
