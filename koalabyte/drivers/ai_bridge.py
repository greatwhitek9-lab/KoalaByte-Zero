"""ESP32-S3 voice-to-AI bridge driver shim.

The EYE1 dual-eye ESP32-S3 board is the default voice front end. It captures
wake-word/audio events from its onboard microphone and forwards transcripts or
voice events to the Jetson-side KoalaByte AI companion runtime.
"""
from __future__ import annotations

from .base import BaseDriver


class AiBridgeDriver(BaseDriver):
    """Validate the EYE1 ESP32-S3 onboard mic to AI companion bridge."""

    name = "ai_bridge"

    def self_test(self):
        bridge = getattr(self.config, "ai_bridge", None)
        audio = getattr(self.config, "audio", None)
        eyes = getattr(self.config, "eyes", None)
        if bridge is None or audio is None or eyes is None:
            return {"name": self.name, "status": "fail", "detail": "missing ai_bridge/audio/eyes config"}

        if getattr(bridge, "controller_ref", None) != "EYE1":
            return {"name": self.name, "status": "fail", "detail": "AI bridge must use EYE1 controller"}
        if getattr(bridge, "default_microphone_ref", None) != "EYE1":
            return {"name": self.name, "status": "fail", "detail": "default voice mic must be EYE1 onboard mic"}
        if getattr(audio, "primary_microphone_ref", None) != "EYE1":
            return {"name": self.name, "status": "fail", "detail": "primary audio mic must resolve to EYE1"}
        if not getattr(audio, "external_microphone_optional", False):
            return {"name": self.name, "status": "fail", "detail": "MIC1 must remain optional/DNP by default"}
        if getattr(bridge, "forwards_to", None) != "KoalaByteCompanion.speak":
            return {"name": self.name, "status": "fail", "detail": "AI bridge must route transcripts to KoalaByteCompanion.speak"}
        if not getattr(bridge, "requires_confirmation_for_actions", False):
            return {"name": self.name, "status": "fail", "detail": "voice actions must require confirmation"}

        route = getattr(bridge, "transcript_route", "EYE1 onboard mic -> AI companion")
        return {"name": self.name, "status": "pass", "detail": route}

    def initialize(self):
        bridge = self.config.ai_bridge
        return (
            f"{self.name}: {bridge.controller_ref} onboard mic routed over "
            f"{bridge.transport} to {bridge.forwards_to}"
        )
