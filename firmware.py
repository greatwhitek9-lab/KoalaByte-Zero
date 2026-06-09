#!/usr/bin/env python3
"""KoalaByte v2.7 Main Firmware Entry Point (fixed)

This update fixes several issues:
- Implements _load_bom_components so components are available.
- Replaces an undefined main() call with a proper main() function.
- Provides a minimal interactive_menu implementation.
- Improves import error messaging and keeps behavior safe for lab mode.
"""
from __future__ import annotations

import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional

# Improved exception handling for dependency imports
try:
    from config import (
        get_hardware_config,
        get_cyberpet_config,
        get_security_config,
        get_ui_config,
    )
    from cyberpet_ai import KillerKoalaCompanion
except ImportError as e:
    # If cyberpet_ai is not present, provide a lightweight stub so firmware can run safely.
    try:
        # Attempt to import an optional local stub
        from . import cyberpet_ai  # type: ignore
    except Exception:
        class KillerKoalaCompanion:  # minimal stub
            def __init__(self, *args, **kwargs):
                pass

    if 'get_hardware_config' not in globals():
        sys.exit(f"Critical Error: Missing module dependencies. Please ensure all dependencies are installed. {e}")

LOG_DIR = Path("/var/log/koalabyte")
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE = LOG_DIR / "firmware.log"
except PermissionError:
    LOG_FILE = Path("./koalabyte_firmware.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger("koalabyte.v2_7")

@dataclass(frozen=True)
class HardwareComponent:
    """BOM-backed hardware component metadata."""

    ref: str
    name: str
    manufacturer: str
    mpn_or_module: str
    interface: str
    mount: str
    notes: str = ""

    def describe(self) -> str:
        return f"{self.ref}: {self.name} | {self.mpn_or_module} | {self.interface}"

class Display:
    """DS1: Generic 3.5 inch HDMI LCD, 5V, Jetson-driven display."""

    def __init__(self, component: HardwareComponent, width: int = 800, height: int = 480):
        self.component = component
        self.width = width
        self.height = height
        self.initialized = False

    def initialize(self) -> None:
        # HDMI display is Jetson-driven; real validation is handled by X/Wayland/DRM stack.
        logger.info("Display initialized: %s (%sx%s target)", self.component.describe(), self.width, self.height)
        self.initialized = True

class Camera:
    """CAM1: (IMX708 CSI camera module)"""

    def __init__(self, component: HardwareComponent, csi_id: int = 0):
        self.component = component
        self.csi_id = csi_id
        self.initialized = False

    def initialize(self) -> None:
        # Production implementation should validate with libcamera, v4l2-ctl, or GStreamer.
        logger.info("Camera initialized: %s on CSI-%s", self.component.describe(), self.csi_id)
        self.initialized = True

class LedRing:
    """WS2812-compatible 16-LED eye ring."""

    def __init__(self, component: HardwareComponent, color_profile: str, led_count: int = 16):
        self.component = component
        self.color_profile = color_profile
        self.led_count = led_count
        self.initialized = False

    def initialize(self) -> None:
        logger.info(
            "LED ring initialized: %s | count=%s | profile=%s",
            self.component.describe(),
            self.led_count,
            self.color_profile,
        )
        self.initialized = True

class BatterySystem:
    """2S2P 21700 Li-ion pack battery system."""

    PACK_FULL_V = 8.40
    PACK_NOMINAL_V = 7.40
    PACK_LOW_WARN_V = 6.60
    PACK_CRITICAL_V = 6.20
    REGULATED_RAIL_V = 5.00
    REGULATED_RAIL_MAX_A = 12.00
    TARGET_ENERGY_WH = 74.0

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
        self._voltage_reader = voltage_reader
        self._temp_reader = temp_reader
        self.initialized = False

    def initialize(self) -> None:
        logger.info("Battery pack: %s", self.pack.describe())
        logger.info("Battery BMS: %s", self.bms.describe())
        logger.info("5V regulator: %s", self.regulator.describe())
        logger.info("Battery fuse: %s", self.fuse.describe())
        logger.info("Battery thermistor: %s", self.thermistor.describe())
        self.initialized = True
        self.log_status()

    def read_pack_voltage(self) -> Optional[float]:
        if self._voltage_reader is None:
            return None
        try:
            return float(self._voltage_reader())
        except Exception as exc:
            logger.warning("Battery voltage read failed: %s", exc)
            return None

    def read_pack_temperature_c(self) -> Optional[float]:
        if self._temp_reader is None:
            return None
        try:
            return float(self._temp_reader())
        except Exception as exc:
            logger.warning("Battery temperature read failed: %s", exc)
            return None

    def estimate_state_of_charge(self, voltage: Optional[float]) -> Optional[int]:
        if voltage is None:
            return None
        # Conservative linear approximation for a 2S Li-ion pack.
        denom = (self.PACK_FULL_V - self.PACK_CRITICAL_V)
        if denom == 0:
            return None
        soc = int(round((voltage - self.PACK_CRITICAL_V) / denom * 100))
        return max(0, min(100, soc))

    def safety_state(self) -> str:
        voltage = self.read_pack_voltage()
        temp_c = self.read_pack_temperature_c()

        if voltage is not None:
            if voltage <= self.PACK_CRITICAL_V:
                return "CRITICAL_LOW_VOLTAGE"
            if voltage <= self.PACK_LOW_WARN_V:
                return "LOW_VOLTAGE_WARNING"

        if temp_c is not None:
            if temp_c < 0 or temp_c > 60:
                return "BATTERY_TEMPERATURE_OUT_OF_RANGE"

        return "OK"

    def log_status(self) -> None:
        voltage = self.read_pack_voltage()
        temp_c = self.read_pack_temperature_c()
        soc = self.estimate_state_of_charge(voltage)
        logger.info(
            "Battery status: voltage=%sV | estimated_soc=%s%% | temp=%sC | state=%s",
            f"{voltage:.2f}" if voltage is not None else "not-wired",
            soc if soc is not None else "unknown",
            f"{temp_c:.1f}" if temp_c is not None else "not-wired",
            self.safety_state(),
        )

class WirelessModule:
    """Wireless/peripheral module wrapper."""

    def __init__(self, component: HardwareComponent):
        self.component = component
        self.initialized = False

    def initialize(self) -> None:
        logger.info("Module initialized: %s", self.component.describe())
        self.initialized = True

class SafetyInterlock:
    """Runtime gate for lab-only functions."""

    def __init__(self, security_config):
        self.security_config = security_config
        self.lab_mode_acknowledged = False

    def acknowledge_lab_mode(self) -> None:
        logger.warning("Lab-only mode acknowledged. Use only on systems you own or are authorized to test.")
        self.lab_mode_acknowledged = True

    def require_lab_mode(self) -> bool:
        if self.security_config and getattr(self.security_config, "LAB_MODE_REQUIRED", False):
            if not self.lab_mode_acknowledged:
                logger.warning("Blocked: lab-only mode has not been acknowledged.")
                return False
        return True

class KoalaByteDevice:
    """Main firmware orchestrator for KoalaByte v2.7."""

    VERSION = "2.7 w/batt"

    def __init__(self):
        try:
            logger.info("Initializing KoalaByte v%s Device...", self.VERSION)

            self.hw_config = get_hardware_config()
            self.pet_config = get_cyberpet_config()
            self.sec_config = get_security_config()
            self.ui_config = get_ui_config()

            self.killerkoala = KillerKoalaCompanion(self.pet_config)
            self.safety = SafetyInterlock(self.sec_config)

            self.components: Dict[str, HardwareComponent] = self._load_bom_components()

            self.display = Display(
                self.components["DS1"],
                width=getattr(self.hw_config, "DISPLAY_WIDTH", 800),
                height=getattr(self.hw_config, "DISPLAY_HEIGHT", 480),
            )
            self.camera = Camera(self.components["CAM1"], csi_id=0)
            self.left_eye = LedRing(self.components["LED_L"], color_profile="ultraviolet/purple")
            self.right_eye = LedRing(self.components["LED_R"], color_profile="cyber green")
            self.battery = BatterySystem(
                pack=self.components["BAT1"],
                bms=self.components["BMS1"],
                regulator=self.components["REG1"],
                fuse=self.components["F1"],
                thermistor=self.components["TH1"],
                test_pads=self.components["TP_BAT"],
            )

            self.esp32s3 = WirelessModule(self.components.get("U2", self.components.get("U_RF1")))
            self.wifi_bt = WirelessModule(self.components["U_RF1"])
            self.nfc = WirelessModule(self.components["U_RF2"])
            self.ble = WirelessModule(self.components["U_RF3"])
            self.subghz = WirelessModule(self.components["U_RF4"])
            self.gps = WirelessModule(self.components["GPS1"])
            self.sdr = WirelessModule(self.components["SDR1"])

            logger.info("KoalaByte Device object created successfully")
        except Exception as e:
            logger.error("Initialization failed: %s", e, exc_info=True)
            sys.exit(1)

    def _load_bom_components(self) -> Dict[str, HardwareComponent]:
        """BOM component map aligned to KoalaByte v2.7 w/batt."""
        # Return a complete mapping of components referenced by the orchestrator.
        return {
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
            "U2": HardwareComponent("U2", "ESP32-S3 Module", "Espressif", "ESP32-S3-WROOM-1", "UART/USB", "Module"),
            "U_RF1": HardwareComponent("U_RF1", "WiFi/Bluetooth Module", "MediaTek", "MT7921K", "M.2", "Internal"),
            "U_RF2": HardwareComponent("U_RF2", "NFC Module", "Elechouse", "PN532", "I2C", "Board"),
            "U_RF3": HardwareComponent("U_RF3", "BLE Module", "Raytac", "nRF52840", "I2C", "Board"),
            "U_RF4": HardwareComponent("U_RF4", "Sub-GHz Module", "Ebyte", "CC1101", "GPIO", "Board"),
            "GPS1": HardwareComponent("GPS1", "GPS Module", "U-Blox", "NEO-M8N", "UART", "Board"),
            "SDR1": HardwareComponent("SDR1", "Software Defined Radio", "RTL-SDR", "RTL2832U", "USB", "Stick"),
        }

    def boot_sequence(self) -> None:
        """Execute device boot sequence."""
        logger.info("=" * 60)
        logger.info("KoalaByte v%s - BOOT SEQUENCE", self.VERSION)
        logger.info("Time: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logger.info("=" * 60)

        steps = [
            ("Initialize display", self.display.initialize),
            ("Initialize camera", self.camera.initialize),
            ("Initialize left LED", self.left_eye.initialize),
            ("Initialize right LED", self.right_eye.initialize),
            ("Initialize battery", self.battery.initialize),
            ("Initialize wifi/bluetooth", self.wifi_bt.initialize),
            ("Initialize NFC", self.nfc.initialize),
            ("Initialize BLE", self.ble.initialize),
            ("Initialize sub-GHz", self.subghz.initialize),
            ("Initialize GPS", self.gps.initialize),
            ("Initialize SDR", self.sdr.initialize),
        ]

        for index, (label, action) in enumerate(steps, start=1):
            logger.info("[%s/%s] %s...", index, len(steps), label)
            try:
                action()
            except Exception as exc:
                logger.warning("Step '%s' failed: %s", label, exc)

    def interactive_menu(self) -> None:
        """Minimal interactive menu for local debugging.

        For automated or headless deployments, this will exit immediately.
        """
        # If we're not attached to a terminal, avoid interactive prompts.
        if not sys.stdin or not sys.stdout or not sys.stdin.isatty():
            logger.info("Headless environment detected; skipping interactive menu.")
            return

        while True:
            print("\nKoalaByte Interactive Menu")
            print("1) Show battery status")
            print("2) Acknowledge lab mode")
            print("3) Exit")
            choice = input("Select: ").strip()
            if choice == "1":
                self.battery.log_status()
            elif choice == "2":
                self.safety.acknowledge_lab_mode()
            elif choice == "3":
                print("Exiting interactive menu.")
                break
            else:
                print("Unknown option")

def main() -> int:
    device = KoalaByteDevice()
    device.boot_sequence()
    # Don't force interactive menu on non-interactive runs
    try:
        device.interactive_menu()
    except Exception:
        logger.debug("Interactive menu failed or aborted", exc_info=True)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
