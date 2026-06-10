from koalabyte.config import CONFIG, as_dict


def test_display_target_is_hdmi_800x480():
    assert CONFIG.display.interface == "HDMI"
    assert CONFIG.display.width == 800
    assert CONFIG.display.height == 480


def test_nfc_coil_is_left_ear():
    assert CONFIG.peripherals.nfc_coil_location == "inside left ear"


def test_power_config_matches_checked_in_bom():
    assert CONFIG.power.battery_ref == "BAT1"
    assert CONFIG.power.battery == "2S2P 21700 Li-ion pack"
    assert CONFIG.power.bms_ref == "BMS1"
    assert CONFIG.power.bms.startswith("2S Li-ion BMS")
    assert CONFIG.power.regulator_ref == "REG1"
    assert CONFIG.power.regulator == "5V 12A synchronous buck regulator module"
    assert CONFIG.power.fuse_ref == "F1"
    assert "2S pack" in CONFIG.power.regulator_path


def test_config_serializes():
    data = as_dict()
    assert data["board"] == "KoalaByte Rev 0.5 Version B"
    assert data["power"]["battery"] == "2S2P 21700 Li-ion pack"
