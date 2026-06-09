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
    interface: str
    notes: str = ""

    def describe(self) -> str:
        return f"{self.ref}: {self.name} ({self.manufacturer}) via {self.interface}"

class Display:
    def __init__(self, component: HardwareComponent, width: int = 800, height: int = 480):
        self.component = component
        self.width = width
        self.height = height

    def initialize(self) -> None:
        logger.info(f"Display [{self.component.describe()}] initialized ({self.width}x{self.height}).")

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
    VERSION = "v2.7 Unified"

    def __init__(self):
        try:
            logger.info("Starting unified KoalaByte firmware...")
            self.hw_config = get_hardware_config()
            self.components: Dict[str, HardwareComponent] = self.load_components()
            self.display = Display(self.components['Display'])
            self.battery = BatterySystem(self.components['Battery'])
            self.killerkoala = KillerKoala(KillerKoalaCompanion(self.hw_config))
            logger.info("KoalaDevice initialized successfully.")
        except Exception as e:
            logger.error("Initialization failed!", exc_info=True)
            sys.exit(1)

    def load_components(self):
        return {
            "Display": HardwareComponent("D1", "Generic HDMI LCD", "HDMI Interface", "Jetson-driven"),
            "Battery": HardwareComponent("BAT1", "2S2P Li-ion", "Custom Connector", "7.4V Nominal"),
        }

    def boot_sequence(self):
        logger.info(f"Executing boot sequence [{self.VERSION}]...")
        self.display.initialize()
        self.battery.monitor()
        self.killerkoala.initialize()

    def run(self):
        self.boot_sequence()
        logger.info("Device is ready and operational.")

    def interactive_menu(self):
        commands = {
            "1": ("Check Battery", self.battery.monitor),
            "2": ("Initialize KillerKoala", self.killerkoala.initialize),
        }

        while True:
            print("\n==== KoalaByte Menu ====")
            for key, (desc, _) in commands.items():
                print(f"[{key}] {desc}")
            choice = input("Select an option (q to quit): ")
            if choice.lower() == 'q':
                break
            elif choice in commands:
                _, func = commands[choice]
                func()
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    device = KoalaDevice()
    device.run()
