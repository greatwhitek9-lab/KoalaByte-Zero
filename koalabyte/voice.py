"""Voice interaction primitives for the KoalaByte companion.

This module keeps speech handling separate from the hardware/runtime layer. The
firmware can feed it text from any speech-to-text engine, then pass the returned
response to a text-to-speech engine or on-screen UI.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable

WAKE_WORD = "KillerKoala"
WAKE_WORD_NORMALIZED = WAKE_WORD.lower()


class VoiceIntent(str, Enum):
    """Safe high-level intents the companion can answer or route."""

    ANSWER = "answer"
    STATUS = "status"
    SELF_TEST = "self_test"
    SHOW_CONFIG = "show_config"
    HELP = "help"
    LISTENING = "listening"
    REFUSE = "refuse"


@dataclass(frozen=True)
class VoiceResponse:
    """Result of a spoken or typed interaction with the AI pet."""

    transcript: str
    intent: VoiceIntent
    response_text: str
    action: str | None = None
    requires_confirmation: bool = False
    wake_word: str = WAKE_WORD
    wake_word_detected: bool = False


class VoiceInteractionEngine:
    """Convert transcribed user speech into companion answers or safe actions."""

    BLOCKED_TERMS = (
        "steal",
        "credential",
        "password dump",
        "persistence",
        "evasion",
        "destroy",
        "wipe",
        "unauthorized",
    )

    def __init__(
        self,
        allowed_actions: Iterable[str] | None = None,
        wake_word: str = WAKE_WORD,
        require_wake_word: bool = True,
    ) -> None:
        self.allowed_actions = set(
            allowed_actions
            or (
                "self_test",
                "show_config",
                "status",
                "help",
            )
        )
        self.wake_word = wake_word
        self.require_wake_word = require_wake_word

    def handle_transcript(
        self,
        transcript: str,
        answer_provider: Callable[[str], str] | None = None,
    ) -> VoiceResponse:
        """Return an answer or an allowlisted action for a speech transcript.

        Commands must begin with the wake word by default. ``answer_provider`` is
        intentionally injected by the caller. That lets the runtime use a local
        model, a cloud model, or a canned fallback without wiring vendor-specific
        code into firmware tests.
        """
        normalized = " ".join(transcript.lower().strip().split())
        if not normalized:
            return VoiceResponse(
                transcript=transcript,
                intent=VoiceIntent.LISTENING,
                response_text=f"Say {self.wake_word} followed by a command.",
                wake_word=self.wake_word,
            )

        wake_word_normalized = self.wake_word.lower()
        wake_word_detected = normalized.startswith(wake_word_normalized)
        if self.require_wake_word and not wake_word_detected:
            return VoiceResponse(
                transcript=transcript,
                intent=VoiceIntent.LISTENING,
                response_text=f"Wake word not detected. Say {self.wake_word} followed by a command.",
                wake_word=self.wake_word,
                wake_word_detected=False,
            )

        command = normalized
        command_text = transcript.strip()
        if wake_word_detected:
            command = normalized[len(wake_word_normalized):].strip(" ,:-")
            command_text = transcript.strip()[len(self.wake_word):].strip(" ,:-")

        if not command:
            return VoiceResponse(
                transcript=transcript,
                intent=VoiceIntent.HELP,
                response_text=f"I am awake. Say {self.wake_word} followed by status, self-test, config, or help.",
                wake_word=self.wake_word,
                wake_word_detected=wake_word_detected,
            )

        if any(term in command for term in self.BLOCKED_TERMS):
            return VoiceResponse(
                transcript=transcript,
                intent=VoiceIntent.REFUSE,
                response_text=(
                    "I can only help with authorized KoalaByte lab tasks, safe device status, "
                    "and configuration guidance."
                ),
                wake_word=self.wake_word,
                wake_word_detected=wake_word_detected,
            )

        if any(phrase in command for phrase in ("self test", "self-test", "run diagnostics")):
            return self._action_response(transcript, VoiceIntent.SELF_TEST, "self_test", wake_word_detected)

        if any(phrase in command for phrase in ("show config", "print config", "configuration")):
            return self._action_response(transcript, VoiceIntent.SHOW_CONFIG, "show_config", wake_word_detected)

        if any(phrase in command for phrase in ("status", "how are you", "battery", "systems")):
            return self._action_response(transcript, VoiceIntent.STATUS, "status", wake_word_detected)

        if any(phrase in command for phrase in ("help", "what can you do", "commands")):
            return VoiceResponse(
                transcript=transcript,
                intent=VoiceIntent.HELP,
                response_text=(
                    f"Say {self.wake_word} followed by status, run self-test, show config, "
                    "or ask a general KoalaByte question."
                ),
                wake_word=self.wake_word,
                wake_word_detected=wake_word_detected,
            )

        answer = answer_provider(command_text) if answer_provider else self._fallback_answer(command_text)
        return VoiceResponse(
            transcript=transcript,
            intent=VoiceIntent.ANSWER,
            response_text=answer,
            wake_word=self.wake_word,
            wake_word_detected=wake_word_detected,
        )

    def _action_response(
        self,
        transcript: str,
        intent: VoiceIntent,
        action: str,
        wake_word_detected: bool,
    ) -> VoiceResponse:
        if action not in self.allowed_actions:
            return VoiceResponse(
                transcript=transcript,
                intent=VoiceIntent.REFUSE,
                response_text=f"That action is not enabled on this KoalaByte build: {action}",
                wake_word=self.wake_word,
                wake_word_detected=wake_word_detected,
            )
        return VoiceResponse(
            transcript=transcript,
            intent=intent,
            response_text=f"Okay. I can run {action.replace('_', ' ')} after confirmation.",
            action=action,
            requires_confirmation=True,
            wake_word=self.wake_word,
            wake_word_detected=wake_word_detected,
        )

    @staticmethod
    def _fallback_answer(prompt: str) -> str:
        return (
            "I heard you. My offline answer mode is active, but no model provider is "
            "connected yet. Route this prompt to a local or cloud model to answer fully: "
            f"{prompt}"
        )
