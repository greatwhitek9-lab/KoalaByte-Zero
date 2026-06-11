"""Eye display driver for the KoalaByte ESP32-S3 dual-eye LCD board."""
from __future__ import annotations

from .base import BaseDriver


class EyeDisplayDriver(BaseDriver):
    """Driver shim for the KoalaByte dual-eye display controller.

    Rev 0.5 Version B uses an ESP32-S3 dual 1.28 inch LCD board for the eyes.
    The self-test accepts the current ``config.eye_display`` schema and keeps
    compatibility with older ``config.eyes`` / ``config.leds`` layouts.
    """

    name = "eyedisplay"

    def _resolve_eye_config(self):
        cfg = getattr(self, "config", None)
        if cfg is None:
            return None

        # Current schema first, then historical aliases used by older CI runs.
        for attr in ("eye_display", "eyes", "eye", "leds"):
            if hasattr(cfg, attr):
                return getattr(cfg, attr)
        return None

    def self_test(self):
        eye_cfg = self._resolve_eye_config()
        if eye_cfg is None:
            return {"name": self.name, "status": "fail", "detail": "no eye display config found"}

        board_ref = getattr(eye_cfg, "board_ref", getattr(eye_cfg, "ref", None))
        board = getattr(eye_cfg, "board", getattr(eye_cfg, "controller", ""))
        brightness = getattr(eye_cfg, "brightness", 1.0)
        legacy_rings = getattr(eye_cfg, "legacy_ws2812_eye_rings", False)

        left_color = getattr(eye_cfg, "left_color", None)
        right_color = getattr(eye_cfg, "right_color", None)
        leds_per_eye = getattr(eye_cfg, "leds_per_eye", getattr(eye_cfg, "pixels_per_eye", None))

        board_name = str(board).lower()
        is_dual_eye_board = (
            "dual" in board_name
            or "double eye" in board_name
            or "duale ye" in board_name.replace("-", " ")
            or "duale" in board_name
        )
        has_valid_ref = board_ref in (None, "EYE1")
        has_valid_brightness = 0 <= brightness <= 1
        has_valid_lcd_config = is_dual_eye_board
        has_valid_legacy_ring_config = legacy_rings or (leds_per_eye is not None and leds_per_eye > 0)
        has_valid_eye_config = has_valid_lcd_config or has_valid_legacy_ring_config

        if left_color is not None:
            has_valid_eye_config = has_valid_eye_config and len(left_color) == 3
        if right_color is not None:
            has_valid_eye_config = has_valid_eye_config and len(right_color) == 3

        ok = has_valid_ref and has_valid_brightness and has_valid_eye_config
        detail = (
            "EYE1 dual-eye board config"
            if ok
            else "expected EYE1 dual-eye board config"
        )
        return {"name": self.name, "status": "pass" if ok else "fail", "detail": detail}


# Backwards-compatible alias for existing imports
LedRingDriver = EyeDisplayDriver
