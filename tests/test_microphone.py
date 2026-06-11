from koalabyte.config import CONFIG, as_dict


def test_right_ear_microphone_is_configured_for_voice_ai_pet():
    assert CONFIG.audio.microphone_ref == "MIC1"
    assert "microphone" in CONFIG.audio.microphone.lower()
    assert CONFIG.audio.microphone_location == "inside right ear"
    assert "voice" in CONFIG.audio.microphone_purpose.lower()

    data = as_dict()
    assert data["audio"]["microphone_ref"] == "MIC1"
    assert data["audio"]["microphone_location"] == "inside right ear"
