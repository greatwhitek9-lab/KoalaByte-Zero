from pathlib import Path

import yaml

from koalabyte.config import CONFIG, as_dict
from koalabyte.main import DRIVERS
from koalabyte.drivers.eye_display import EyeDisplayDriver
from koalabyte.drivers.ledring import LedRingDriver


def _structured_bom_refs():
    bom_path = Path(__file__).resolve().parents[1] / "docs" / "bom.yaml"
    with bom_path.open("r", encoding="utf-8") as handle:
        bom = yaml.safe_load(handle)
    return {item["ref"] for item in bom}


def _structured_bom_by_ref():
    bom_path = Path(__file__).resolve().parents[1] / "docs" / "bom.yaml"
    with bom_path.open("r", encoding="utf-8") as handle:
        bom = yaml.safe_load(handle)
    return {item["ref"]: item for item in bom}


def _tab_bom_text():
    bom_path = Path(__file__).resolve().parents[1] / "docs" / "BOM"
    return bom_path.read_text(encoding="utf-8")


def test_display_target_is_hdmi_800x480():
    assert CONFIG.display.interface == "HDMI"
    assert CONFIG.display.width == 800
    assert CONFIG.display.height == 480


def test_eye_config_uses_esp32_s3_dual_eye_board():
    bom = _structured_bom_by_ref()
    assert CONFIG.eyes.ref == "EYE1"
    assert "ESP32-S3 1.28inch Double Eye Round LCD AIoT Development Board" in CONFIG.eyes.controller
    assert "Onboard Dual 1.28inch IPS Displays" in CONFIG.eyes.controller
    assert CONFIG.eye_display.board_ref == "EYE1"
    assert CONFIG.eye_display.legacy_ws2812_eye_rings is False
    assert "EYE1" in bom
    assert "LED_L" not in bom
    assert "LED_R" not in bom
    assert "U2" not in bom
    assert bom["EYE1"]["mpn"] == CONFIG.eyes.controller


def test_production_bom_does_not_include_standalone_esp32_wroom():
    bom_refs = _structured_bom_refs()
    bom_text = _tab_bom_text()
    assert "U2" not in bom_refs
    assert "ESP32-S3-WROOM" not in bom_text
    assert "ESP32-S3-WROOM" not in "\n".join(
        f"{item['ref']} {item.get('mpn', '')} {item.get('notes', '')}"
        for item in _structured_bom_by_ref().values()
    )


def test_runtime_uses_eye_display_driver_not_led_ring_driver():
    driver_names = {driver.__name__ for driver in DRIVERS}
    assert "EyeDisplayDriver" in driver_names
    assert "LedRingDriver" not in driver_names
    assert EyeDisplayDriver in DRIVERS
    result = EyeDisplayDriver(CONFIG).self_test()
    assert result["status"] == "pass"
    assert "EYE1" in result["detail"]
    assert "LED_L/LED_R" in result["detail"]


def test_legacy_ledring_alias_accepts_canonical_config():
    result = LedRingDriver(CONFIG).self_test()
    assert result["status"] == "pass"
    assert "EYE1" in result["detail"]
    assert "LED_L/LED_R" in result["detail"]


def test_camera_is_centered_above_eyes_below_ears():
    bom = _structured_bom_by_ref()
    assert CONFIG.camera.location == "centered just above eyes and below ears"
    assert "centered just above eyes and below ears" in bom["CAM1"]["notes"]
    assert "Right-eye camera" not in bom["CAM1"]["notes"]


def test_nfc_coil_is_left_ear():
    assert CONFIG.peripherals.nfc_coil_location == "inside left ear"


def test_button_config_has_no_nose_switch():
    button_data = CONFIG.peripherals.buttons.__dict__
    assert "nose_switch_gpio" not in button_data


def test_power_config_matches_checked_in_bom():
    assert CONFIG.power.battery_ref == "BAT1"
    assert CONFIG.power.battery == "2S2P 21700 Li-ion pack"
    assert CONFIG.power.bms_ref == "BMS1"
    assert CONFIG.power.bms.startswith("2S Li-ion BMS")
    assert CONFIG.power.charger_ref == "J_CHG"
    assert "8.4V CC/CV" in CONFIG.power.charger
    assert "2A-4A" in CONFIG.power.charger
    assert CONFIG.power.regulator_ref == "REG1"
    assert CONFIG.power.regulator == "5V 12A synchronous buck regulator module"
    assert CONFIG.power.power_input_ref == "J_USB"
    assert CONFIG.power.fuse_ref == "F1"
    assert CONFIG.power.power_switch_ref == "SW_PWR"
    assert CONFIG.power.power_switch_location == "back of device"
    assert "rear switch" in CONFIG.power.regulator_path


def test_power_config_refs_resolve_in_structured_bom():
    bom_refs = _structured_bom_refs()
    config_refs = {
        CONFIG.power.battery_ref,
        CONFIG.power.bms_ref,
        CONFIG.power.charger_ref,
        CONFIG.power.regulator_ref,
        CONFIG.power.power_input_ref,
        CONFIG.power.fuse_ref,
        CONFIG.power.power_switch_ref,
    }
    assert config_refs <= bom_refs


def test_config_serializes():
    data = as_dict()
    assert data["board"] == "KoalaByte Rev 0.5 Version B"
    assert data["power"]["battery"] == "2S2P 21700 Li-ion pack"
    assert data["power"]["charger_ref"] == "J_CHG"
    assert data["power"]["power_switch_ref"] == "SW_PWR"
    assert data["camera"]["location"] == "centered just above eyes and below ears"
    assert data["eyes"]["ref"] == "EYE1"
    assert data["eye_display"]["legacy_ws2812_eye_rings"] is False
