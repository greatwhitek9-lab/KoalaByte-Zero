#!/usr/bin/env python3
"""KoalaByte Unified Firmware v2.7 Main Entry Point
This script consolidates all hardware initialization, AI companion, and critical modules based on the hardware BOM file.

Added: integration with KillerKoala companion and SafetyInterlock (BOM-aligned).
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Callable, Dict, Optional
from dataclasses import dataclass

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
    # Allow static analysis / CI without runtime deps
    KillerKoalaCompanion = None
    def _missing_config_exit():
        sys.exit(f"Critical Error: Missing dependencies (config or cyberpet_ai). {e}")

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
    mpn_or_module: str
    interface: str
    mount: str
    notes: str = ""

    def describe(self) -> str:
        return (
            f"{self.ref}: {self.name} | Manufacturer: {self.manufacturer}, "
            f"Module/Part: {self.mpn_or_module}, Interface: {self.interface}"
        )

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
    def __init__(self, companion: "KillerKoalaCompanion"):
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
            # These functions may raise ImportError if config module isn't present at runtime
            self.hw_config = get_hardware_config()
            self.pet_config = get_cyberpet_config()
            self.sec_config = get_security_config()
            self.ui_config = get_ui_config()
        except Exception:
            # Use defaults and log but don't hard-fail here so offline analysis can proceed
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

        # Major subsystems
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
            test_pads=self.components['TP_BAT']
        )

        self.wifi_bt = WirelessModule(self.components['U_RF1'])
        self.nfc = WirelessModule(self.components['U_RF2'])
        self.ble = WirelessModule(self.components['U_RF3'])
        self.subghz = WirelessModule(self.components['U_RF4'])
        self.gps = WirelessModule(self.components['GPS1'])
        self.sdr = WirelessModule(self.components['SDR1'])

        # Safety interlock
        self.safety = SafetyInterlock(self.sec_config)

        # Initialize KillerKoala companion if available
        companion_instance = None
        if self.pet_config is not None and KillerKoalaCompanion is not None:
            try:
                companion_instance = KillerKoalaCompanion(self.pet_config)
            except Exception as e:
                logger.warning("Failed to instantiate KillerKoalaCompanion: %s", e)
        elif KillerKoalaCompanion is None:
            logger.debug("KillerKoalaCompanion class not available in this environment.")

        self.killerkoala = KillerKoala(companion_instance)

        logger.info("KoalaByte Initialization Complete.")

    def _load_bom_components(self) -> Dict[str, HardwareComponent]:
        """Parse docs/BOM and return a mapping of ref -> HardwareComponent.

        Expected BOM format (tab-separated columns):
        Ref\tQty\tManufacturer/Series\tMPN / Module\tFootprint strategy\tMount\tNotes
        """
        bom_path = Path(__file__).parent / "docs" / "BOM"
        components: Dict[str, HardwareComponent] = {}

        if not bom_path.exists():
            logger.warning("BOM file not found at %s; falling back to minimal placeholder components.", bom_path)
            # Minimal placeholders to avoid KeyError later
            placeholders = ["DS1", "CAM1", "LED_L", "LED_R", "BAT1", "BMS1", "REG1", "F1", "TH1", "TP_BAT", "U_RF1", "U_RF2", "U_RF3", "U_RF4", "GPS1", "SDR1"]
            for ref in placeholders:
                components[ref] = HardwareComponent(ref, ref, "Unknown", "", "", "Unknown")
            return components

        try:
            text = bom_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error("Failed to read BOM file: %s", e)
            return {}

        lines = [ln for ln in text.splitlines() if ln.strip()]
        # Skip header if present
        header = lines[0] if lines else ""
        start_index = 1 if header.lower().startswith("ref") else 0

        for ln in lines[start_index:]:
            cols = [c.strip() for c in ln.split("\t")]
            if not cols or len(cols) < 1:
                continue
            ref = cols[0]
            # Derive fields with safe indexing
            manufacturer = cols[2] if len(cols) > 2 else ""
            mpn = cols[3] if len(cols) > 3 else ""
            footprint = cols[4] if len(cols) > 4 else ""
            mount = cols[5] if len(cols) > 5 else ""
            notes = cols[6] if len(cols) > 6 else ""

            # Name: prefer MPN/Module column if descriptive, otherwise manufacturer or ref
            name = mpn or manufacturer or ref

            components[ref] = HardwareComponent(
                ref=ref,
                name=name,
                manufacturer=manufacturer,
                mpn_or_module=mpn,
                interface=footprint,
                mount=mount,
                notes=notes,
            )

        # Ensure critical keys exist (BOM may omit optional rows); fill placeholders if missing
        critical = ["DS1", "CAM1", "LED_L", "LED_R", "BAT1", "BMS1", "REG1", "F1", "TH1", "TP_BAT", "U_RF1", "U_RF2", "U_RF3", "U_RF4", "GPS1", "SDR1"]
        for ref in critical:
            if ref not in components:
                components[ref] = HardwareComponent(ref, ref, "Unknown", "", "", "Unknown")

        logger.info("Loaded %d components from BOM", len(components))
        return components

    def initialize_subsystems(self):
        """Perform initialization of all subsystems and the AI companion."""
        self.display.initialize()
        self.camera.initialize()
        self.left_eye.initialize()
        self.right_eye.initialize()
        self.battery.initialize()
        self.wifi_bt.initialize()
        self.nfc.initialize()
        self.ble.initialize()
        self.subghz.initialize()
        self.gps.initialize()
        self.sdr.initialize()

        # Initialize safety and companion
        if self.killerkoala is not None:
            self.killerkoala.initialize()
        else:
            logger.warning("KillerKoala wrapper is not present; skipping companion initialization.")

if __name__ == "__main__":
    # Instantiate device where BOM will be parsed from docs/BOM
    device = KoalaByteDevice()
    device.initialize_subsystems()
