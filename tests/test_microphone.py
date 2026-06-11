from koalabyte.config import CONFIG, as_dict


def test_right_ear_microphone_is_configured_for_voice_ai_pet():
    """Keep MIC1 compatibility while EYE1 remains the default AI voice mic."""
    assert CONFIG.audio.primary_microphone_ref == "EYE1"
    assert "onboard microphone" in CONFIG.audio.primary_microphone.lower()
    assert "wake-word" in CONFIG.audio.primary_microphone_purpose.lower()

    # Backward-compatible optional external microphone aliases.
    assert CONFIG.audio.microphone_ref == "MIC1"
    assert CONFIG.audio.external_microphone_ref == "MIC1"
    assert CONFIG.audio.external_microphone_optional is True
    assert CONFIG.audio.microphone_optional is True
    assert "microphone" in CONFIG.audio.microphone.lower()
    assert CONFIG.audio.microphone_location == "inside right ear"
    assert "voice" in CONFIG.audio.microphone_purpose.lower()
    assert "DNP" in CONFIG.audio.microphone_install

    data = as_dict()
    assert data["audio"]["primary_microphone_ref"] == "EYE1"
    assert data["audio"]["microphone_ref"] == "MIC1"
    assert data["audio"]["external_microphone_ref"] == "MIC1"
    assert data["audio"]["external_microphone_optional"] is True
    assert data["audio"]["microphone_location"] == "inside right ear"
