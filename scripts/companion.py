"""
KillerKoala - AI Cyberpet Companion Engine

Refactored for errors, redundancies, and clarity. Features:
- Gruff, cynical personality that levels up with each penetration testing action.
"""

import json
import random
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum, auto

try:
    from config import CyberpetConfig, get_cyberpet_config
except ImportError:
    # Fallback for module imports
    try:
        from firmware.config import CyberpetConfig, get_cyberpet_config
    except Exception:
        # Minimal stand-in config
        @dataclass
        class CyberpetConfig:
            DIALOGUE_IDLE: List[str] = field(default_factory=lambda: ["...Killerkoala is silent..."])
            DIALOGUE_WIFI_SCAN: List[str] = field(default_factory=lambda: ["Scanning... bah."])
            DIALOGUE_NFC: List[str] = field(default_factory=lambda: ["NFC ping."])
            DIALOGUE_LOW_BATTERY: List[str] = field(default_factory=lambda: ["Plug me in."])
            XP_REWARDS: Dict[str, int] = field(default_factory=lambda: {"wifi_scan": 5})
            XP_TO_LEVEL: int = 100
            XP_MULTIPLIER: float = 1.25
            PERSONALITY_TIERS: Dict[str, Tuple[int, int]] = field(default_factory=lambda: {"noob": (1, 4)})
            MAX_LEVEL: int = 99

        def get_cyberpet_config():
            return CyberpetConfig()


class Mood(Enum):
    IDLE = auto()
    ACTIVE = auto()
    HUNGRY = auto()
    AGGRESSIVE = auto()
    LEGENDARY = auto()


class PersonalityTier(Enum):
    NOOB = auto()
    HACKER = auto()
    ELITE = auto()
    LEGEND = auto()


@dataclass
class CyberpetStats:
    level: int = 1
    experience: int = 0
    mood: Mood = Mood.IDLE
    personality_tier: PersonalityTier = PersonalityTier.NOOB

    # Skill stats
    network_skill: int = 1
    wireless_skill: int = 1
    sensor_skill: int = 1
    memory_skill: int = 1
    hacker_skill: int = 1
    adaptation: int = 0

    # Action counters
    wifi_scans: int = 0
    ble_discoveries: int = 0
    ir_transmissions: int = 0
    nfc_clones: int = 0
    exploits_executed: int = 0
    total_actions: int = 0

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_action_at: str = field(default_factory=lambda: datetime.now().isoformat())

    mood_duration_seconds: int = 30


class KillerKoalaCompanion:
    def __init__(self, config: Optional[CyberpetConfig] = None):
        self.config = config or get_cyberpet_config()
        self.stats = CyberpetStats()
        self._mood_timer = 0
        self._animation_frame = 0
        self.dialogue = self._init_dialogue_banks()

    def _init_dialogue_banks(self) -> Dict[str, List[str]]:
        return {
            "idle": getattr(self.config, 'DIALOGUE_IDLE', ["..."] ),
            "wifi_scan": getattr(self.config, 'DIALOGUE_WIFI_SCAN', ["Scanning..."]),
            "nfc": getattr(self.config, 'DIALOGUE_NFC', ["NFC..."]),
            "low_battery": getattr(self.config, 'DIALOGUE_LOW_BATTERY', ["Plug me in."]),
        }

    def report_action(self, action_type: str, success: bool = True) -> Tuple[int, str]:
        if not success:
            return 0, "Nice try, choom. That didn't work."
        xp_gained = getattr(self.config, 'XP_REWARDS', {}).get(action_type, 5)
        xp_multiplier = 1.0 + 0.1 * (self.stats.level - 1)
        xp_gained = int(xp_gained * xp_multiplier)
        self.stats.experience += xp_gained
        old_level = self.stats.level
        self._check_level_up()
        if hasattr(self.stats, action_type):
            setattr(self.stats, action_type, getattr(self.stats, action_type) + 1)
        self.stats.total_actions += 1
        self.stats.last_action_at = datetime.now().isoformat()
        self.stats.mood = Mood.ACTIVE
        response = self._generate_response(action_type, xp_gained)
        if old_level < self.stats.level:
            response += f"\n[Killerkoala leveled up to {self.stats.level}!]"
        return xp_gained, response

    def _check_level_up(self):
        xp_needed = self._xp_for_next_level()
        if self.stats.experience >= xp_needed:
            self.stats.level += 1
            self.stats.experience %= xp_needed
            self.stats.personality_tier = self._update_personality_tier()
            if self.stats.level >= getattr(self.config, 'MAX_LEVEL', 99):
                self.stats.level = getattr(self.config, 'MAX_LEVEL', 99)
                self.stats.mood = Mood.LEGENDARY

    def _xp_for_next_level(self) -> int:
        base_xp = getattr(self.config, 'XP_TO_LEVEL', 100)
        multiplier = getattr(self.config, 'XP_MULTIPLIER', 1.25)
        return int(base_xp * (multiplier ** (self.stats.level - 1)))

    def _update_personality_tier(self) -> PersonalityTier:
        tiers = getattr(self.config, 'PERSONALITY_TIERS', {})
        for tier, levels in tiers.items():
            if levels[0] <= self.stats.level <= levels[1]:
                return PersonalityTier[tier.upper()]
        return self.stats.personality_tier

    def _generate_response(self, action_type: str, xp_gained: int) -> str:
        dialogue = self.dialogue.get(action_type, [])
        commentary = random.choice(dialogue) if dialogue else "Hmm."
        return f"{commentary} [+{xp_gained} XP]"
