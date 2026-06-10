"""Runtime safety checks for KoalaByte."""
from __future__ import annotations

import os

from .config import CONFIG

LAB_MODE_ENV = "KOALABYTE_LAB_MODE"


class SafetyError(RuntimeError):
    """Raised when firmware is started outside an authorized lab context."""


def lab_mode_enabled() -> bool:
    return os.getenv(LAB_MODE_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def assert_safe_runtime() -> None:
    """Require explicit lab mode unless disabled in config."""
    if CONFIG.safety.lab_mode_required and not lab_mode_enabled():
        raise SafetyError(
            f"{CONFIG.safety.safety_banner} Set {LAB_MODE_ENV}=1 only in an authorized lab."
        )


def allowed_capability(name: str) -> bool:
    return name not in CONFIG.safety.disabled_actions
