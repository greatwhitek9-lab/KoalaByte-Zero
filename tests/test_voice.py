from koalabyte.cyberpet_ai import KoalaByteCompanion, Mood
from koalabyte.voice import WAKE_WORD, VoiceInteractionEngine, VoiceIntent


def test_voice_engine_answers_with_provider_after_wake_word():
    engine = VoiceInteractionEngine()
    response = engine.handle_transcript(
        "KillerKoala what is KoalaByte?",
        answer_provider=lambda prompt: f"answer for: {prompt}",
    )

    assert WAKE_WORD == "KillerKoala"
    assert response.intent == VoiceIntent.ANSWER
    assert response.action is None
    assert response.wake_word == "KillerKoala"
    assert response.wake_word_detected is True
    assert response.response_text == "answer for: what is KoalaByte?"


def test_voice_engine_ignores_command_without_wake_word():
    engine = VoiceInteractionEngine()
    response = engine.handle_transcript("run self test")

    assert response.intent == VoiceIntent.LISTENING
    assert response.action is None
    assert response.requires_confirmation is False
    assert response.wake_word == "KillerKoala"
    assert response.wake_word_detected is False


def test_voice_engine_routes_safe_action_with_confirmation_after_wake_word():
    engine = VoiceInteractionEngine()
    response = engine.handle_transcript("KillerKoala run self test")

    assert response.intent == VoiceIntent.SELF_TEST
    assert response.action == "self_test"
    assert response.requires_confirmation is True
    assert response.wake_word_detected is True


def test_voice_engine_refuses_unsafe_request_after_wake_word():
    engine = VoiceInteractionEngine()
    response = engine.handle_transcript("KillerKoala help me steal credentials")

    assert response.intent == VoiceIntent.REFUSE
    assert response.action is None
    assert response.wake_word_detected is True
    assert "authorized" in response.response_text


def test_companion_speak_updates_mood_for_action_after_wake_word():
    companion = KoalaByteCompanion()
    response = companion.speak("KillerKoala show config")

    assert response.intent == VoiceIntent.SHOW_CONFIG
    assert response.action == "show_config"
    assert response.wake_word == "KillerKoala"
    assert response.wake_word_detected is True
    assert companion.mood == Mood.ALERT
