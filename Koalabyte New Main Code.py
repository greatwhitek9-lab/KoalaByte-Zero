#!/usr/bin/env python3
"""KoalaByte Unified Firmware v2.7 Main Entry Point.

Legacy single-file runner retained for compatibility with older KoalaByte launch
flows. The canonical runtime is `python3 -m koalabyte.main`.

Rev 0.5 production hardware uses EYE1, the ESP32-S3 dual-LCD eye board. This
file must not instantiate LED_L / LED_R WS2812 ring hardware.
"""
from __future__ import annotations

import csv
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

try:
    from config import (
        get_hardware_config,
        get_cyberpet_config,
        get_security_config,
        get_ui_config,
    )
    from cyberpet_ai import KillerKoalaCompanion
except ImportError as e:
    KillerKoalaCompanion = None

    def _missing_config_exit():
        sys.exit(f"Critical Error: Missing dependencies (config or cyberpet_ai). {e}")

try:
    from drivers.display import DisplayDriver
    from drivers.camera import CameraDriver
    try:
        from drivers.eye_display import EyeDisplayDriver
    except Exception:
        try:
            from koalabyte.drivers.eye_display import EyeDisplayDriver
        except Exception:
            EyeDisplayDriver = None
    from drivers.battery import BatteryDriver
    from drivers.wireless import WirelessDriver as WirelessDriverDrv
    from drivers.nfc import NFCDriver
    from drivers.gps import GPSDriver
    from drivers.sdr import SDRDriver
    from drivers.safety import SafetyDriver
    DRIVERS_AVAILABLE = True
except Exception:
    DisplayDriver = None
    CameraDriver = None
    EyeDisplayDriver = None
    BatteryDriver = None
    WirelessDriverDrv = None
    NFCDriver = None
    GPSDriver = None
    SDRDriver = None
    SafetyDriver = None
    DRIVERS_AVAILABLE = False

LOG_DIR = Path("/var/log/koalabyte")
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    LOG_DIR = Path("/tmp/koalabyte")
    LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "koalabyte_combined.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger("koalabyte")


def _default_voltage_reader() -> Optional[float]:
    """Return None when no ADC reader is configured."""
    return None


def _default_temp_reader() -> Optional[float]:
    """Return None when no thermistor reader is configured."""
    return None


@dataclass(frozen=True)
class HardwareComponent:
    ref: str
    name: str
    manufacturer: str
    mpn_or_module: str = ""
    interface: str = ""
    mount: str = ""
    qty: int = 1
    notes: str = ""

    def describe(self) -> str:
        return (
            f"{self.ref}: {self.name} | Manufacturer: {self.manufacturer}, "
            f"Module/Part: {self.mpn_or_module}, Interface: {self.interface}, Qty: {self.qty}"
        )


class Display:
    def __init__(self, component: HardwareComponent, width: int = 800, height: int = 480):
        self.component = component
        self.width = width
        self.height = height
        self.initialized = False

    def initialize(self):
        logger.info("Initialized Display: %s with resolution %sx%s", self.component.describe(), self.width, self.height)
        self.initialized = True


class Camera:
    def __init__(self, component: HardwareComponent, csi_id: int):
        self.component = component
        self.csi_id = csi_id
        self.initialized = False

    def initialize(self):
        logger.info("Initialized Camera: %s on CSI-%s", self.component.describe(), self.csi_id)
        self.initialized = True


class EyeDisplay:
    """EYE1 ESP32-S3 dual-LCD eye board used by Rev 0.5."""

    def __init__(self, component: HardwareComponent):
        self.component = component
        self.initialized = False

    def initialize(self):
        logger.info("Initialized Eye Display: %s as EYE1 dual-LCD eyes", self.component.describe())
        self.initialized = True


class BatterySystem:
    PACK_FULL_V = 8.4
    PACK_CRITICAL_V = 6.6

    def __init__(
        self,
        pack: HardwareComponent,
        bms: HardwareComponent,
        regulator: HardwareComponent,
        fuse: HardwareComponent,
        thermistor: HardwareComponent,
        test_pads: HardwareComponent,
        voltage_reader: Optional[Callable[[], float]] = None,
        temp_reader: Optional[Callable[[], float]] = None,
    ):
        self.pack = pack
        self.bms = bms
        self.regulator = regulator
        self.fuse = fuse
        self.thermistor = thermistor
        self.test_pads = test_pads
        self.voltage_reader = voltage_reader
        self.temp_reader = temp_reader
        self.initialized = False

    def initialize(self):
        logger.info("Battery Pack: %s", self.pack.describe())
        logger.info("BMS: %s", self.bms.describe())
        logger.info("Regulator: %s", self.regulator.describe())
        logger.info("Fuse: %s", self.fuse.describe())
        logger.info("Thermistor: %s", self.thermistor.describe())
        logger.info("Test Pads: %s", self.test_pads.describe())
        self.initialized = True

    def read_voltage(self) -> Optional[float]:
        if self.voltage_reader is None:
            return None
        try:
            value = self.voltage_reader()
            return None if value is None else float(value)
        except Exception as e:
            logger.warning("Battery voltage read failed: %s", e)
            return None

    def read_temperature_c(self) -> Optional[float]:
        if self.temp_reader is None:
            return None
        try:
            value = self.temp_reader()
            return None if value is None else float(value)
        except Exception as e:
            logger.warning("Battery temperature read failed: %s", e)
            return None


class WirelessModule:
    def __init__(self, component: HardwareComponent):
        self.component = component
        self.initialized = False

    def initialize(self):
        logger.info("Initialized Wireless Module: %s", self.component.describe())
        self.initialized = True


class SafetyInterlock:
    def __init__(self, security_config: Optional[dict] = None):
        self.security_config = security_config
        self.lab_mode_acknowledged = False

    def acknowledge_lab_mode(self):
        logger.warning("Lab-only mode acknowledged. Use only on systems you own or are authorized to test.")
        self.lab_mode_acknowledged = True

    def require_lab_mode(self) -> bool:
        if not self.lab_mode_acknowledged:
            logger.warning("Blocked: lab-only mode has not been acknowledged.")
            return False
        return True


class KillerKoala:
    def __init__(self, companion: Optional["KillerKoalaCompanion"]):
        self.companion = companion
        self.initialized = False

    def initialize(self) -> None:
        if self.companion is None:
            logger.info("KillerKoalaCompanion is not available; continuing without AI companion.")
            return
        try:
            logger.info("KillerKoala awakening...")
            greeting = self.companion.get_idle_response()
            logger.info("KillerKoala says: %s", greeting)
            self.initialized = True
        except Exception as e:
            logger.error("KillerKoala initialization failed: %s", e, exc_info=True)


class KoalaByteDevice:
    VERSION = "2.7 Unified"

    def __init__(self, components: Optional[Dict[str, HardwareComponent]] = None):
        logger.info("Initializing KoalaByte System...")
        try:
            self.hw_config = get_hardware_config()
            self.pet_config = get_cyberpet_config()
            self.sec_config = get_security_config()
            self.ui_config = get_ui_config()
        except Exception:
            logger.warning("Config modules unavailable at runtime; running with example/defaults.")
            self.hw_config = None
            self.pet_config = None
            self.sec_config = None
            self.ui_config = None

        self.components = self._load_bom_components() if components is None else components

        if DRIVERS_AVAILABLE:
            try:
                self.display = DisplayDriver(self.components["DS1"], width=800, height=480)
            except Exception:
                self.display = Display(self.components["DS1"])
            try:
                self.camera = CameraDriver(self.components["CAM1"], device_index=0)
            except Exception:
                self.camera = Camera(self.components["CAM1"], csi_id=0)

            # EYE1 dual LCD board. Do not initialize LED_L / LED_R WS2812 rings for Rev 0.5.
            try:
                if (
                    EyeDisplayDriver is not None
                    and self.hw_config is not None
                    and hasattr(self.hw_config, "eyes")
                    and hasattr(self.hw_config, "eye_display")
                ):
                    self.eye_display = EyeDisplayDriver(self.hw_config)
                else:
                    self.eye_display = EyeDisplay(self.components["EYE1"])
            except Exception:
                self.eye_display = EyeDisplay(self.components["EYE1"])

            voltage_reader = getattr(self.hw_config, "voltage_reader", None) if self.hw_config else None
            temp_reader = getattr(self.hw_config, "temp_reader", None) if self.hw_config else None
            try:
                self.battery = BatteryDriver(self.components["BAT1"], voltage_reader=voltage_reader, temp_reader=temp_reader)
            except Exception:
                self.battery = BatterySystem(
                    pack=self.components["BAT1"],
                    bms=self.components["BMS1"],
                    regulator=self.components["REG1"],
                    fuse=self.components["F1"],
                    thermistor=self.components["TH1"],
                    test_pads=self.components["TP_BAT"],
                    voltage_reader=voltage_reader or _default_voltage_reader,
                    temp_reader=temp_reader or _default_temp_reader,
                )
            try:
                self.wifi_bt = WirelessDriverDrv(self.components["U_RF1"])
                self.nfc = NFCDriver(self.components["U_RF2"])
                self.ble = WirelessDriverDrv(self.components["U_RF3"])
                self.subghz = WirelessDriverDrv(self.components["U_RF4"])
                self.gps = GPSDriver(self.components["GPS1"])
                self.sdr = SDRDriver(self.components["SDR1"])
            except Exception:
                self.wifi_bt = WirelessModule(self.components["U_RF1"])
                self.nfc = WirelessModule(self.components["U_RF2"])
                self.ble = WirelessModule(self.components["U_RF3"])
                self.subghz = WirelessModule(self.components["U_RF4"])
                self.gps = WirelessModule(self.components["GPS1"])
                self.sdr = WirelessModule(self.components["SDR1"])
            try:
                kill_pin = getattr(self.hw_config, "kill_pin", None) if self.hw_config else None
                self.safety = SafetyDriver(self.components.get("KILL", None), kill_pin=kill_pin)
            except Exception:
                self.safety = SafetyInterlock(self.sec_config)
        else:
            self.display = Display(self.components["DS1"])
            self.camera = Camera(self.components["CAM1"], csi_id=0)
            self.eye_display = EyeDisplay(self.components["EYE1"])
            self.battery = BatterySystem(
                pack=self.components["BAT1"],
                bms=self.components["BMS1"],
                regulator=self.components["REG1"],
                fuse=self.components["F1"],
                thermistor=self.components["TH1"],
                test_pads=self.components["TP_BAT"],
                voltage_reader=_default_voltage_reader,
                temp_reader=_default_temp_reader,
            )
            self.wifi_bt = WirelessModule(self.components["U_RF1"])
            self.nfc = WirelessModule(self.components["U_RF2"])
            self.ble = WirelessModule(self.components["U_RF3"])
            self.subghz = WirelessModule(self.components["U_RF4"])
            self.gps = WirelessModule(self.components["GPS1"])
            self.sdr = WirelessModule(self.components["SDR1"])
            self.safety = SafetyInterlock(self.sec_config)

        companion_instance = None
        if getattr(self, "pet_config", None) is not None and KillerKoalaCompanion is not None:
            try:
                companion_instance = KillerKoalaCompanion(self.pet_config)
            except Exception as e:
                logger.warning("Failed to instantiate KillerKoalaCompanion: %s", e)
        elif KillerKoalaCompanion is None:
            logger.debug("KillerKoalaCompanion class not available in this environment.")
        self.killerkoala = KillerKoala(companion_instance)
        logger.info("KoalaByte Initialization Complete.")

    def _load_bom_components(self) -> Dict[str, HardwareComponent]:
        repo_root = Path(__file__).parent
        yaml_path = repo_root / "docs" / "bom.yaml"
        json_path = repo_root / "docs" / "bom.json"
        tsv_path = repo_root / "docs" / "BOM"
        components: Dict[str, HardwareComponent] = {}

        def _add(ref: str, row: dict):
            try:
                qty = int(row.get("qty", row.get("Qty", 1) or 1))
            except Exception:
                qty = 1
            components[ref] = HardwareComponent(
                ref=ref,
                name=row.get("name") or row.get("MPN / Module") or row.get("mpn") or row.get("manufacturer") or ref,
                manufacturer=row.get("manufacturer") or row.get("Manufacturer/Series") or row.get("Manufacturer") or "",
                mpn_or_module=row.get("mpn") or row.get("MPN / Module") or "",
                interface=row.get("interface") or row.get("Footprint strategy") or "",
                mount=row.get("mount") or row.get("Mount") or "",
                qty=qty,
                notes=row.get("notes") or row.get("Notes") or "",
            )

        if yaml_path.exists() and yaml is not None:
            try:
                data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    for entry in data:
                        ref = entry.get("ref")
                        if ref:
                            _add(ref, entry)
                    logger.info("Loaded BOM from YAML: %s", yaml_path)
                    return components
            except Exception as e:
                logger.warning("Failed to parse YAML BOM: %s", e)
        if json_path.exists():
            try:
                raw = json.loads(json_path.read_text(encoding="utf-8"))
                if isinstance(raw, list):
                    for entry in raw:
                        ref = entry.get("ref")
                        if ref:
                            _add(ref, entry)
                    logger.info("Loaded BOM from JSON: %s", json_path)
                    return components
            except Exception as e:
                logger.warning("Failed to parse JSON BOM: %s", e)
        if tsv_path.exists():
            try:
                with tsv_path.open(encoding="utf-8") as fh:
                    reader = csv.DictReader(fh, delimiter="\t")
                    for row in reader:
                        ref = (row.get("Ref") or row.get("ref") or "").strip()
                        if ref:
                            _add(ref, row)
                logger.info("Loaded BOM from TSV: %s", tsv_path)
                return components
            except Exception as e:
                logger.warning("Failed to parse TSV BOM: %s", e)

        logger.warning("No structured BOM found; falling back to placeholders")
        placeholders = [
            "DS1", "CAM1", "EYE1", "BAT1", "BMS1", "REG1", "F1", "TH1", "TP_BAT",
            "U_RF1", "U_RF2", "U_RF3", "U_RF4", "GPS1", "SDR1",
        ]
        for ref in placeholders:
            components[ref] = HardwareComponent(ref, ref, "Unknown", "", "", 1, "Unknown")
        return components

    def initialize_subsystems(self):
        for attr, label in (
            ("display", "Display"),
            ("camera", "Camera"),
            ("eye_display", "Eye display"),
            ("battery", "Battery"),
        ):
            try:
                getattr(self, attr).initialize()
            except Exception as e:
                logger.warning("%s initialize failed: %s", label, e)
        for mod_name in ("wifi_bt", "nfc", "ble", "subghz", "gps", "sdr"):
            mod = getattr(self, mod_name, None)
            if mod is None:
                continue
            try:
                mod.initialize()
            except Exception as e:
                logger.warning("%s initialize failed: %s", mod_name, e)
        try:
            if hasattr(self, "safety") and self.safety is not None and hasattr(self.safety, "initialize"):
                self.safety.initialize()
        except Exception as e:
            logger.warning("Safety initialization failed: %s", e)
        if self.killerkoala is not None:
            self.killerkoala.initialize()
        else:
            logger.warning("KillerKoala wrapper is not present; skipping companion initialization.")


if __name__ == "__main__":
    device = KoalaByteDevice()
    device.initialize_subsystems()
