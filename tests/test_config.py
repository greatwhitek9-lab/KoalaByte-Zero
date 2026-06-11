from pathlib import Path

import yaml

from koalabyte.config import CONFIG, as_dict


def _structured_bom():
    bom_path = Path(__file__).resolve().parents[1] / "docs" / "bom.yaml"
    with bom_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _structured_bom_refs():
    return {item["ref"] for item in _structured_bom()}


def _structured_bom_refs_and_aliases():
    refs = set()
    for item in _structured_bom():
        refs.add(item["ref"])
        refs.update(item.get("aliases", []))
    return refs


def _structured_bom_by_ref():
    return {item["ref"]: item for item in _structured_bom()}


def _split_ref_tokens(ref: str) -> set[str]:
    """Return concrete BOM tokens from composite config refs like PWR1/BAT1."""
    return {token.strip() for token in ref.split("/") if token.strip()}


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
    assert bom["EYE1"]["mpn"] == CONFIG.eyes.controller


def test_nfc_coil_is_left_ear():
    assert CONFIG.peripherals.nfc_coil_location == "inside left ear"


def test_power_config_matches_checked_in_bom():
    assert CONFIG.power.battery_ref == "PWR1/BAT1"
    assert "USB-C PD power bank" in CONFIG.power.battery
    assert "2S Li-ion pack" in CONFIG.power.battery
    assert CONFIG.power.bms_ref == "BMS1"
    assert CONFIG.power.bms.startswith("2S Li-ion BMS")
    assert CONFIG.power.charger_ref == "J_CHG"
    assert "8.4V CC/CV" in CONFIG.power.charger
    assert "2A-4A" in CONFIG.power.charger
    assert CONFIG.power.regulator_ref == "REG1"
    assert CONFIG.power.regulator == "5V 10-12A synchronous buck regulator module"
    assert CONFIG.power.power_input_ref == "J_USB/J11"
    assert CONFIG.power.fuse_ref == "F1"
    assert "2S pack" in CONFIG.power.regulator_path


def test_power_config_refs_resolve_in_structured_bom():
    bom_refs = _structured_bom_refs_and_aliases()
    config_refs = {
        CONFIG.power.battery_ref,
        CONFIG.power.bms_ref,
        CONFIG.power.charger_ref,
        CONFIG.power.regulator_ref,
        CONFIG.power.power_input_ref,
        CONFIG.power.fuse_ref,
    }
    for ref in config_refs:
        assert _split_ref_tokens(ref) <= bom_refs


def test_config_serializes():
    data = as_dict()
    assert data["board"] == "KoalaByte Zero Rev 0.5 Version B"
    assert "2S Li-ion pack" in data["power"]["battery"]
    assert data["power"]["charger_ref"] == "J_CHG"
    assert data["eyes"]["ref"] == "EYE1"
    assert data["eye_display"]["legacy_ws2812_eye_rings"] is False
