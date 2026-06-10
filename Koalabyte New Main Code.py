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
    # Fail fast if these are required for runtime; allow module to be imported for static analysis
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

    def __init__(self, components: Dict[str, HardwareComponent]):
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

        # Map components based on BOM provided
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
        if 'pet_config' in locals() and self.pet_config is not None and KillerKoalaCompanion is not None:
            try:
                companion_instance = KillerKoalaCompanion(self.pet_config)
            except Exception as e:
                logger.warning("Failed to instantiate KillerKoalaCompanion: %s", e)
        elif KillerKoalaCompanion is None:
            logger.debug("KillerKoalaCompanion class not available in this environment.")

        self.killerkoala = KillerKoala(companion_instance)

        logger.info("KoalaByte Initialization Complete.")

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
    # Example BOM Component Initialization
    example_bom = {
        "DS1": HardwareComponent("DS1", "3.5 inch HDMI Display", "Generic", "HDMI LCD", "HDMI", "Panel Mount"),
        "CAM1": HardwareComponent("CAM1", "IMX708 CSI Camera", "Arducam", "IMX708", "CSI", "Board Mount"),
        "LED_L": HardwareComponent("LED_L", "Left LED Ring", "Custom", "WS2812B", "GPIO", "Ring Mount"),
        "LED_R": HardwareComponent("LED_R", "Right LED Ring", "Custom", "WS2812B", "GPIO", "Ring Mount"),
        "BAT1": HardwareComponent("BAT1", "Li-ion Battery Pack", "Custom", "2S2P 21700", "XT30", "Battery Bay"),
        "BMS1": HardwareComponent("BMS1", "Battery Management System", "Generic", "2S BMS", "Connector", "Inline"),
        "REG1": HardwareComponent("REG1", "5V Regulator", "Murata", "DC-DC", "High Current", "PCB Mount"),
        "F1": HardwareComponent("F1", "10A Fuse", "Littelfuse", "Resettable", "PC Mount", "Inline Safety"),
        "TH1": HardwareComponent("TH1", "Thermistor", "TDK", "10k NTC", "Lead", "Temperature Sensor"),
        "TP_BAT": HardwareComponent("TP_BAT", "Test Pads", "Custom", "Pads", "SMD", "Voltage Reads"),
        "U_RF1": HardwareComponent("U_RF1", "WiFi/Bluetooth Module", "MediaTek", "MT7921K", "M.2", "Internal"),
        "U_RF2": HardwareComponent("U_RF2", "NFC Module", "Elechouse", "PN532", "I2C", "Board"),
        "U_RF3": HardwareComponent("U_RF3", "BLE Module", "Raytac", "nRF52840", "I2C", "Board"),
        "U_RF4": HardwareComponent("U_RF4", "Sub-GHz Module", "Ebyte", "CC1101", "GPIO", "Board"),
        "GPS1": HardwareComponent("GPS1", "GPS Module", "U-Blox", "NEO-M8N", "UART", "Board"),
        "SDR1": HardwareComponent("SDR1", "Software Defined Radio", "RTL-SDR", "RTL2832U", "USB", "Stick"),
    }

    # Instantiate device with example BOM and initialize
    device = KoalaByteDevice(example_bom)
    device.initialize_subsystems()
