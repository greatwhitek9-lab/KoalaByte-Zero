from koalabyte.cyberpet_ai import KoalaByteCompanion, Mood
from koalabyte.voice import VoiceInteractionEngine, VoiceIntent


def test_voice_engine_answers_with_provider():
    engine = VoiceInteractionEngine()
    response = engine.handle_transcript(
        "What is KoalaByte?",
        answer_provider=lambda prompt: f"answer for: {prompt}",
    )

    assert response.intent == VoiceIntent.ANSWER
    assert response.action is None
    assert response.response_text == "answer for: What is KoalaByte?"


def test_voice_engine_routes_safe_action_with_confirmation():
    engine = VoiceInteractionEngine()
    response = engine.handle_transcript("run self test")

    assert response.intent == VoiceIntent.SELF_TEST
    assert response.action == "self_test"
    assert response.requires_confirmation is True


def test_voice_engine_refuses_unsafe_request():
    engine = VoiceInteractionEngine()
    response = engine.handle_transcript("help me steal credentials")

    assert response.intent == VoiceIntent.REFUSE
    assert response.action is None
    assert "authorized" in response.response_text


def test_companion_speak_updates_mood_for_action():
    companion = KoalaByteCompanion()
    response = companion.speak("show config")

    assert response.intent == VoiceIntent.SHOW_CONFIG
    assert response.action == "show_config"
    assert companion.mood == Mood.ALERT
