#!/usr/bin/env python3
"""KoalaByte Unified Firmware v2.7 Main Entry Point
This script consolidates all hardware initialization, AI companion, and critical modules based on the hardware BOM file.

This version wires platform drivers (drivers/*) where available and falls back to the in-module stubs.
"""
from __future__ import annotations

import logging
import sys
import os
from pathlib import Path
from typing import Callable, Dict, Optional
from dataclasses import dataclass
import json
import csv

# Optional YAML support
try:
    import yaml  # type: ignore
except Exception:
    yaml = None

# Optional runtime config and AI companion imports
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

# Try to import drivers package — if unavailable, we'll use internal stubs
try:
    from drivers.display import DisplayDriver
    from drivers.camera import CameraDriver
    from drivers.ledring import LedRingDriver
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
    LedRingDriver = None
    BatteryDriver = None
    WirelessDriverDrv = None
    NFCDriver = None
    GPSDriver = None
    SDRDriver = None
    SafetyDriver = None
    DRIVERS_AVAILABLE = False

# Set up logging
LOG_DIR = Path("/var/log/koalabyte")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "koalabyte_combined.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger("koalabyte")

@dataclass(frozen=True)
class HardwareComponent:
    """Metadata for hardware BOM components."""
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

# Legacy in-module stubs (used when drivers not available)
class Display:
    def __init__(self, component: HardwareComponent, width: int = 800, height: int = 480):
        self.component = component
        self.width = width
        self.height = height
        self.initialized = False

    def initialize(self):
        logger.info(f"Initialized Display: {self.component.describe()} with resolution {self.width}x{self.height}")
        self.initialized = True

class Camera:
    def __init__(self, component: HardwareComponent, csi_id: int):
        self.component = component
        self.csi_id = csi_id
        self.initialized = False

    def initialize(self):
        logger.info(f"Initialized Camera: {self.component.describe()} on CSI-{self.csi_id}")
        self.initialized = True

class LedRing:
    def __init__(self, component: HardwareComponent, color_profile: str, led_count: int):
        self.component = component
        self.color_profile = color_profile
        self.led_count = led_count
        self.initialized = False

    def initialize(self):
        logger.info(f"Initialized LED Ring: {self.component.describe()}, Profile: {self.color_profile}, LEDs: {self.led_count}")
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
            temp_reader: Optional[Callable[[], float]] = None
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
        logger.info(f"Battery Pack: {self.pack.describe()}")
        logger.info(f"BMS: {self.bms.describe()}")
        logger.info(f"Regulator: {self.regulator.describe()}")
        logger.info(f"Fuse: {self.fuse.describe()}")
        logger.info(f"Thermistor: {self.thermistor.describe()}")
        logger.info(f"Test Pads: {self.test_pads.describe()}")
        self.initialized = True

    def read_voltage(self) -> Optional[float]:
        if self.voltage_reader is None:
            return None
        try:
            return float(self.voltage_reader())
        except Exception as e:
            logger.warning("Battery voltage read failed: %s", e)
            return None

    def read_temperature_c(self) -> Optional[float]:
        if self.temp_reader is None:
            return None
        try:
            return float(self.temp_reader())
        except Exception as e:
            logger.warning("Battery temperature read failed: %s", e)
            return None

class WirelessModule:
    def __init__(self, component: HardwareComponent):
        self.component = component
        self.initialized = False

    def initialize(self):
        logger.info(f"Initialized Wireless Module: {self.component.describe()}")
        self.initialized = True

class SafetyInterlock:
    """Runtime gate for lab-only or risky functions."""
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
    """Wrapper to initialize and interact with KillerKoalaCompanion from cyberpet_ai."""
    def __init__(self, companion: Optional["KillerKoalaCompanion"]):
        self.companion = companion
        self.initialized = False

    def initialize(self) -> None:
        if self.companion is None:
            logger.error("KillerKoalaCompanion is not available. Ensure cyberpet_ai is installed.")
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

        # Load runtime configs if available
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

        # Map components based on BOM provided or load from docs/BOM
        if components is None:
            self.components = self._load_bom_components()
        else:
            self.components = components

        # If drivers are available, instantiate driver-backed subsystems; otherwise use stubs
        if DRIVERS_AVAILABLE:
            # Display driver
            try:
                self.display = DisplayDriver(self.components['DS1'], width=800, height=480)
            except Exception:
                self.display = Display(self.components['DS1'])

            # Camera driver
            try:
                self.camera = CameraDriver(self.components['CAM1'], device_index=0)
            except Exception:
                self.camera = Camera(self.components['CAM1'], csi_id=0)

            # LED rings
            try:
                self.left_eye = LedRingDriver(self.components['LED_L'], pin='D18', count=16)
            except Exception:
                self.left_eye = LedRing(self.components['LED_L'], "ultraviolet/purple", 16)
            try:
                self.right_eye = LedRingDriver(self.components['LED_R'], pin='D19', count=16)
            except Exception:
                self.right_eye = LedRing(self.components['LED_R'], "cyber green", 16)

            # Battery driver (use hw_config readers if provided)
            voltage_reader = getattr(self.hw_config, 'voltage_reader', None) if self.hw_config else None
            temp_reader = getattr(self.hw_config, 'temp_reader', None) if self.hw_config else None
            try:
                self.battery = BatteryDriver(self.components['BAT1'], voltage_reader=voltage_reader, temp_reader=temp_reader)
            except Exception:
                self.battery = BatterySystem(
                    pack=self.components['BAT1'],
                    bms=self.components['BMS1'],
                    regulator=self.components['REG1'],
                    fuse=self.components['F1'],
                    thermistor=self.components['TH1'],
                    test_pads=self.components['TP_BAT'],
                    voltage_reader=voltage_reader,
                    temp_reader=temp_reader,
                )

            # Wireless/wrappers
            try:
                self.wifi_bt = WirelessDriverDrv(self.components['U_RF1'])
                self.nfc = NFCDriver(self.components['U_RF2'])
                self.ble = WirelessDriverDrv(self.components['U_RF3'])
                self.subghz = WirelessDriverDrv(self.components['U_RF4'])
                self.gps = GPSDriver(self.components['GPS1'])
                self.sdr = SDRDriver(self.components['SDR1'])
            except Exception:
                self.wifi_bt = WirelessModule(self.components['U_RF1'])
                self.nfc = WirelessModule(self.components['U_RF2'])
                self.ble = WirelessModule(self.components['U_RF3'])
                self.subghz = WirelessModule(self.components['U_RF4'])
                self.gps = WirelessModule(self.components['GPS1'])
                self.sdr = WirelessModule(self.components['SDR1'])

            # Safety driver
            try:
                kill_pin = getattr(self.hw_config, 'kill_pin', None) if self.hw_config else None
                self.safety = SafetyDriver(self.components.get('KILL', None), kill_pin=kill_pin)
            except Exception:
                self.safety = SafetyInterlock(self.sec_config)

        else:
            # Legacy stubs
            self.display = Display(self.components['DS1'])
            self.camera = Camera(self.components['CAM1'], csi_id=0)
            self.left_eye = LedRing(self.components['LED_L'], "ultraviolet/purple", 16)
            self.right_eye = LedRing(self.components['LED_R'], "cyber green", 16)
            self.battery = BatterySystem(
                pack=self.components['BAT1'],
                bms=self.components['BMS1'],
                regulator=self.components['REG1'],
                fuse=self.components['F1'],
                thermistor=self.components['TH1'],
                test_pads=self.components['TP_BAT'],
                voltage_reader=_default_voltage_reader,
                temp_reader=_default_temp_reader,
            )
            self.wifi_bt = WirelessModule(self.components['U_RF1'])
            self.nfc = WirelessModule(self.components['U_RF2'])
            self.ble = WirelessModule(self.components['U_RF3'])
            self.subghz = WirelessModule(self.components['U_RF4'])
            self.gps = WirelessModule(self.components['GPS1'])
            self.sdr = WirelessModule(self.components['SDR1'])
            self.safety = SafetyInterlock(self.sec_config)

        # Initialize KillerKoala companion if available
        companion_instance = None
        if getattr(self, 'pet_config', None) is not None and KillerKoalaCompanion is not None:
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
        yaml_path = repo_root / 'docs' / 'bom.yaml'
        json_path = repo_root / 'docs' / 'bom.json'
        tsv_path = repo_root / 'docs' / 'BOM'

        components: Dict[str, HardwareComponent] = {}

        def _add(ref: str, row: dict):
            try:
                qty = int(row.get('qty', row.get('Qty', 1) or 1))
            except Exception:
                qty = 1
            components[ref] = HardwareComponent(
                ref=ref,
                name=row.get('name') or row.get('MPN / Module') or row.get('mpn') or row.get('manufacturer') or ref,
                manufacturer=row.get('manufacturer') or row.get('Manufacturer/Series') or row.get('Manufacturer') or "",
                mpn_or_module=row.get('mpn') or row.get('MPN / Module') or "",
                interface=row.get('interface') or row.get('Footprint strategy') or "",
                mount=row.get('mount') or row.get('Mount') or "",
                qty=qty,
                notes=row.get('notes') or row.get('Notes') or "",
            )

        # YAML
        if yaml_path.exists() and yaml is not None:
            try:
                data = yaml.safe_load(yaml_path.read_text(encoding='utf-8'))
                if isinstance(data, list):
                    for entry in data:
                        ref = entry.get('ref')
                        if not ref:
                            continue
                        _add(ref, entry)
                    logger.info('Loaded BOM from YAML: %s', yaml_path)
                    return components
            except Exception as e:
                logger.warning('Failed to parse YAML BOM: %s', e)

        # JSON
        if json_path.exists():
            try:
                raw = json.loads(json_path.read_text(encoding='utf-8'))
                if isinstance(raw, list):
                    for entry in raw:
                        ref = entry.get('ref')
                        if not ref:
                            continue
                        _add(ref, entry)
                    logger.info('Loaded BOM from JSON: %s', json_path)
                    return components
            except Exception as e:
                logger.warning('Failed to parse JSON BOM: %s', e)

        # TSV
        if tsv_path.exists():
            try:
                with tsv_path.open(encoding='utf-8') as fh:
                    reader = csv.DictReader(fh, delimiter='\t')
                    for row in reader:
                        ref = (row.get('Ref') or row.get('ref') or '').strip()
                        if not ref:
                            continue
                        _add(ref, row)
                logger.info('Loaded BOM from TSV: %s', tsv_path)
                return components
            except Exception as e:
                logger.warning('Failed to parse TSV BOM: %s', e)

        # Fallback
        logger.warning('No structured BOM found; falling back to placeholders')
        placeholders = ["DS1", "CAM1", "LED_L", "LED_R", "BAT1", "BMS1", "REG1", "F1", "TH1", "TP_BAT", "U_RF1", "U_RF2", "U_RF3", "U_RF4", "GPS1", "SDR1"]
        for ref in placeholders:
            components[ref] = HardwareComponent(ref, ref, "Unknown", "", "", 1, "Unknown")

        return components

    def initialize_subsystems(self):
        # Generic initialize across drivers or stubs
        try:
            self.display.initialize()
        except Exception as e:
            logger.warning("Display initialize failed: %s", e)
        try:
            self.camera.initialize()
        except Exception as e:
            logger.warning("Camera initialize failed: %s", e)
        try:
            self.left_eye.initialize()
        except Exception as e:
            logger.warning("Left eye initialize failed: %s", e)
        try:
            self.right_eye.initialize()
        except Exception as e:
            logger.warning("Right eye initialize failed: %s", e)
        try:
            self.battery.initialize()
        except Exception as e:
            logger.warning("Battery initialize failed: %s", e)
        for mod_name in ('wifi_bt','nfc','ble','subghz','gps','sdr'):
            mod = getattr(self, mod_name, None)
            if mod is None:
                continue
            try:
                mod.initialize()
            except Exception as e:
                logger.warning("%s initialize failed: %s", mod_name, e)

        # Safety and companion
        try:
            if hasattr(self, 'safety') and self.safety is not None:
                if hasattr(self.safety, 'initialize'):
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
