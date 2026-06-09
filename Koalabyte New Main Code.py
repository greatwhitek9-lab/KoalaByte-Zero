#!/usr/bin/env python3
"""KoalaByte Unified Firmware v2.7 Main Entry Point
Consolidates hardware initialization, AI companion, and critical modules.
"""
from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional

try:
    from config import (
        get_hardware_config,
        get_cyberpet_config,
        get_security_config,
        get_ui_config,
    )
    from cyberpet_ai import KillerKoalaCompanion
except ImportError as e:
    sys.exit(f"Critical Error: Missing dependencies. {e}")

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
    """Defines properties of a hardware component."""
    ref: str
    name: str
    manufacturer: str
    mpn_or_module: str = ""
    interface: str = ""
    mount: str = ""
    notes: str = ""

    def describe(self) -> str:
        return f"{self.ref}: {self.name} ({self.manufacturer}) | {self.mpn_or_module} | {self.interface}"

class InfraredSystem:
    def __init__(self, receiver: HardwareComponent, transmitter: HardwareComponent, driver: HardwareComponent):
        self.receiver = receiver
        self.transmitter = transmitter
        self.driver = driver
        self.initialized = False

    def initialize(self):
        logger.info(f"Initializing IR Receiver: {self.receiver.describe()}")
        logger.info(f"Initializing IR Transmitter: {self.transmitter.describe()}")
        logger.info(f"Initializing Driver: {self.driver.describe()}")
        self.initialized = True

class Display:
    def __init__(self, component: HardwareComponent, width: int = 800, height: int = 480):
        self.component = component
        self.width = width
        self.height = height
        self.initialized = False

    def initialize(self) -> None:
        logger.info(f"Display [{self.component.describe()}] initialized ({self.width}x{self.height}).")
        self.initialized = True

class Camera:
    def __init__(self, component: HardwareComponent, csi_id: int = 0):
        self.component = component
        self.csi_id = csi_id
        self.initialized = False

    def initialize(self) -> None:
        logger.info(f"Camera [{self.component.describe()}] initialized on CSI-{self.csi_id}.")
        self.initialized = True

class LedRing:
    def __init__(self, component: HardwareComponent, color_profile: str, led_count: int = 16):
        self.component = component
        self.color_profile = color_profile
        self.led_count = led_count
        self.initialized = False

    def initialize(self) -> None:
        logger.info(
            f"LED ring [{self.component.describe()}] initialized | count={self.led_count} | profile={self.color_profile}")
        self.initialized = True

class BatterySystem:
    def __init__(
        self,
        component: HardwareComponent,
        max_voltage: float = 8.4,
        voltage_reader: Optional[Callable[[], float]] = None,
    ):
        self.component = component
        self.max_voltage = max_voltage
        self._voltage_reader = voltage_reader

    def monitor(self) -> None:
        logger.info(f"Battery [{self.component.describe()}] monitoring active.")

    def read_voltage(self) -> Optional[float]:
        if self._voltage_reader is None:
            return None
        try:
            return float(self._voltage_reader())
        except Exception as e:
            logger.warning("Battery voltage read failed: %s", e)
            return None

    def voltage_status(self) -> str:
        voltage = self.read_voltage()
        if voltage is None:
            return "Unknown"
        if voltage < 6.6:
            return "Critical Voltage"
        return "Voltage Normal"

class WirelessModule:
    def __init__(self, component: HardwareComponent):
        self.component = component
        self.initialized = False

    def initialize(self) -> None:
        logger.info(f"Wireless Module [{self.component.describe()}] initialized.")
        self.initialized = True

class SafetyInterlock:
    def __init__(self, security_config):
        self.security_config = security_config
        self.lab_mode_acknowledged = False

    def acknowledge_lab_mode(self) -> None:
        logger.warning("Lab-only mode acknowledged.")
        self.lab_mode_acknowledged = True

    def require_lab_mode(self) -> bool:
        if not self.lab_mode_acknowledged:
            logger.warning("Operation blocked: lab-only mode not acknowledged.")
            return False
        return True

class KillerKoala:
    def __init__(self, companion: KillerKoalaCompanion):
        self.companion = companion

    def initialize(self) -> None:
        try:
            logger.info("KillerKoala awakening...")
            greeting = self.companion.get_idle_response()
            logger.info(f"KillerKoala says: {greeting}")
        except Exception as e:
            logger.error("KillerKoala initialization failed: %s", e, exc_info=True)

class KoalaDevice:
    VERSION = "2.7 Unified"

    def __init__(self):
        try:
            logger.info("Initializing KoalaByte firmware...")

            self.hw_config = get_hardware_config()
            self.components: Dict[str, HardwareComponent] = self._load_bom_components()

            self.display = Display(self.components['DS1'])
            self.camera = Camera(self.components['CAM1'])
            self.left_eye = LedRing(self.components['LED_L'], "purple")
            self.right_eye = LedRing(self.components['LED_R'], "green")

            self.ir_system = InfraredSystem(
                receiver=self.components['IR_RX1'],
                transmitter=self.components['IR_TX1'],
                driver=self.components['Q_IR1']
            )

            self.battery = BatterySystem(self.components['BAT1'], voltage_reader=None)

            self.esp32s3 = WirelessModule(self.components['U2'])
            self.wifi_bt = WirelessModule(self.components['U_RF1'])
            self.nfc = WirelessModule(self.components['U_RF2'])

            self.killerkoala = KillerKoala(KillerKoalaCompanion(self.hw_config))
            self.safety = SafetyInterlock(get_security_config())

            logger.info("KoalaDevice initialized successfully.")
        except Exception as e:
            logger.error("Initialization failed: %s", e, exc_info=True)
            sys.exit(1)

    def _load_bom_components(self):
        return {
            "DS1": HardwareComponent("DS1", "Display", "Generic", "3.5"),
            "CAM1": HardwareComponent("CAM1", "IMX219 Camera", "Sony", "MIPI-CSI"),
            "LED_L": HardwareComponent("LED_L", "Left LED", "WS2812B", ""),
            "IR_RX1": HardwareComponent("IR_RX1", "Infrared Receiver", "Vishay", "TSOP38238"),
            "IR_TX1": HardwareComponent("IR_TX1", "Infrared Transmitter", "Vishay", "TSAL6200"),
            "Q_IR1": HardwareComponent("Q_IR1", "MOSFET Driver", "ON Semiconductor", "2N7002"),
        }

if __name__ == "__main__":
    device = KoalaDevice()
    logger.info("Running device...")
    device.ir_system.initialize()
    device.run()