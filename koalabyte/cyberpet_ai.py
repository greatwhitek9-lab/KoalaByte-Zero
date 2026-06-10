"""KoalaByte companion personality scaffold.

This module intentionally contains safe assistant behavior only. Offensive workflows must be
implemented as authorized-lab plugins behind the runtime safety gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Mood(str, Enum):
    READY = "ready"
    CURIOUS = "curious"
    ALERT = "alert"
    SLEEPY = "sleepy"


class PersonalityTier(str, Enum):
    NOOB = "noob"
    HACKER = "hacker"
    ELITE = "elite"


@dataclass
class CompanionStatus:
    mood: Mood
    tier: PersonalityTier
    message: str


class KoalaByteCompanion:
    """Small stateful companion used by the main firmware loop."""

    def __init__(self) -> None:
        self.mood = Mood.READY
        self.tier = PersonalityTier.NOOB
        self.experience = 0

    def boot_message(self) -> CompanionStatus:
        return CompanionStatus(
            mood=self.mood,
            tier=self.tier,
            message="KoalaByte online. Lab-safe systems check initialized.",
        )

    def add_experience(self, points: int) -> CompanionStatus:
        self.experience = max(0, self.experience + points)
        if self.experience >= 1000:
            self.tier = PersonalityTier.ELITE
        elif self.experience >= 250:
            self.tier = PersonalityTier.HACKER
        return CompanionStatus(
            mood=self.mood,
            tier=self.tier,
            message=f"Experience updated: {self.experience}",
        )

    def explain_guardrail(self) -> str:
        return "Authorized lab mode only. KoalaByte will not assist unauthorized access."
