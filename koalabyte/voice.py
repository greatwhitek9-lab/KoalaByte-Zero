"""Voice interaction primitives for the KoalaByte companion.

This module keeps speech handling separate from the hardware/runtime layer. The
firmware can feed it text from any speech-to-text engine, then pass the returned
response to a text-to-speech engine or on-screen UI.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable


class VoiceIntent(str, Enum):
    """Safe high-level intents the companion can answer or route."""

    ANSWER = "answer"
    STATUS = "status"
    SELF_TEST = "self_test"
    SHOW_CONFIG = "show_config"
    HELP = "help"
    REFUSE = "refuse"


@dataclass(frozen=True)
class VoiceResponse:
    """Result of a spoken or typed interaction with the AI pet."""

    transcript: str
    intent: VoiceIntent
    response_text: str
    action: str | None = None
    requires_confirmation: bool = False


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

    def __init__(self, allowed_actions: Iterable[str] | None = None) -> None:
        self.allowed_actions = set(
            allowed_actions
            or (
                "self_test",
                "show_config",
                "status",
                "help",
            )
        )

    def handle_transcript(
        self,
        transcript: str,
        answer_provider: Callable[[str], str] | None = None,
    ) -> VoiceResponse:
        """Return an answer or an allowlisted action for a speech transcript.

        ``answer_provider`` is intentionally injected by the caller. That lets the
        runtime use a local model, a cloud model, or a canned fallback without
        wiring vendor-specific code into firmware tests.
        """
        normalized = " ".join(transcript.lower().strip().split())
        if not normalized:
            return VoiceResponse(
                transcript=transcript,
                intent=VoiceIntent.HELP,
                response_text="I did not catch that. Try asking for status, self-test, config, or help.",
            )

        if any(term in normalized for term in self.BLOCKED_TERMS):
            return VoiceResponse(
                transcript=transcript,
                intent=VoiceIntent.REFUSE,
                response_text=(
                    "I can only help with authorized KoalaByte lab tasks, safe device status, "
                    "and configuration guidance."
                ),
            )

        if any(phrase in normalized for phrase in ("self test", "self-test", "run diagnostics")):
            return self._action_response(transcript, VoiceIntent.SELF_TEST, "self_test")

        if any(phrase in normalized for phrase in ("show config", "print config", "configuration")):
            return self._action_response(transcript, VoiceIntent.SHOW_CONFIG, "show_config")

        if any(phrase in normalized for phrase in ("status", "how are you", "battery", "systems")):
            return self._action_response(transcript, VoiceIntent.STATUS, "status")

        if any(phrase in normalized for phrase in ("help", "what can you do", "commands")):
            return VoiceResponse(
                transcript=transcript,
                intent=VoiceIntent.HELP,
                response_text=(
                    "You can ask me for status, run self-test, show config, or ask a general "
                    "KoalaByte question. Actions stay inside authorized lab mode."
                ),
            )

        answer = answer_provider(transcript) if answer_provider else self._fallback_answer(transcript)
        return VoiceResponse(
            transcript=transcript,
            intent=VoiceIntent.ANSWER,
            response_text=answer,
        )

    def _action_response(self, transcript: str, intent: VoiceIntent, action: str) -> VoiceResponse:
        if action not in self.allowed_actions:
            return VoiceResponse(
                transcript=transcript,
                intent=VoiceIntent.REFUSE,
                response_text=f"That action is not enabled on this KoalaByte build: {action}",
            )
        return VoiceResponse(
            transcript=transcript,
            intent=intent,
            response_text=f"Okay. I can run {action.replace('_', ' ')} after confirmation.",
            action=action,
            requires_confirmation=True,
        )

    @staticmethod
    def _fallback_answer(prompt: str) -> str:
        return (
            "I heard you. My offline answer mode is active, but no model provider is "
            "connected yet. Route this prompt to a local or cloud model to answer fully: "
            f"{prompt}"
        )
