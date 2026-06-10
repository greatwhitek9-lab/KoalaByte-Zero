from koalabyte.config import CONFIG, as_dict


def test_display_target_is_hdmi_800x480():
    assert CONFIG.display.interface == "HDMI"
    assert CONFIG.display.width == 800
    assert CONFIG.display.height == 480


def test_nfc_coil_is_left_ear():
    assert CONFIG.peripherals.nfc_coil_location == "inside left ear"


def test_config_serializes():
    data = as_dict()
    assert data["board"] == "KoalaByte Rev 0.5 Version B"
