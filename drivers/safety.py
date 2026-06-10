"""Safety driver (kill switch / interlock) using GPIO where available; simulated fallback.
"""
from __future__ import annotations

import logging

logger = logging.getLogger("koalabyte.drivers.safety")

try:
    from gpiozero import Button
    _HAS_GPIOZERO = True
except Exception:
    _HAS_GPIOZERO = False

class SafetyDriver:
    def __init__(self, component, kill_pin: int = None):
        self.component = component
        self.kill_pin = kill_pin
        self.kill_switch = None
        self.initialized = False

    def initialize(self) -> bool:
        logger.info("SafetyDriver: initializing %s", getattr(self.component, 'describe', lambda: str(self.component))())
        if _HAS_GPIOZERO and self.kill_pin is not None:
            try:
                self.kill_switch = Button(self.kill_pin)
                logger.info("SafetyDriver: kill switch attached to pin %s", self.kill_pin)
                self.initialized = True
                return True
            except Exception as e:
                logger.warning("SafetyDriver: gpio init failed: %s", e)
        logger.info("SafetyDriver: simulated fallback (no physical kill switch)")
        self.initialized = True
        return False

    def is_killed(self) -> bool:
        if self.kill_switch is None:
            return False
        try:
            return self.kill_switch.is_pressed
        except Exception:
            return False

    def shutdown(self):
        self.initialized = False
