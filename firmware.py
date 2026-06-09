#!/usr/bin/env python3
"""KoalaByte v2.7 Main Firmware Entry Point (with splash screen)

This update adds a splash/boot screen shown at startup before the interactive menu
or main UI is presented. The splash image is loaded from ./assets/koalabyte_logo.png if present;
otherwise a cyberpunk koala logo is generated at runtime using Pillow and saved to assets/koalabyte_logo.png.

The display implementation uses pygame when available; it falls back to logging if the
environment is headless or pygame is not installed.
"""
from __future__ import annotations

import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional

# Optional UI/image libs
try:
    import pygame
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False

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

ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
KOALA_LOGO_PATH = ASSETS_DIR / "koalabyte_logo.png"

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


class SplashScreen:
    """Simple splash screen handler using pygame + Pillow.

    If pygame is unavailable or the environment is headless, this is a no-op that logs instead.
    The default generated logo is a cyberpunk angry koala face with neon green and purple eyes on a black background.
    """

    def __init__(self, width: int, height: int, splash_path: Optional[Path] = None):
        self.width = width
        self.height = height
        self.splash_path = splash_path or KOALA_LOGO_PATH

    def _generate_cyberpunk_koala(self) -> Image.Image:
        # Create a black background
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 255))
        draw = ImageDraw.Draw(img)

        cx = self.width // 2
        cy = self.height // 2
        face_radius = min(self.width, self.height) // 3

        # Draw face base (dark gray)
        face_bbox = [cx - face_radius, cy - face_radius, cx + face_radius, cy + face_radius]
        draw.ellipse(face_bbox, fill=(30, 30, 30, 255))

        # Ears
        ear_radius = face_radius // 1.6
        left_ear = [cx - face_radius - ear_radius // 2, cy - face_radius, cx - face_radius + ear_radius, cy - face_radius + ear_radius]
        right_ear = [cx + face_radius - ear_radius, cy - face_radius, cx + face_radius + ear_radius // 2, cy - face_radius + ear_radius]
        draw.ellipse(left_ear, fill=(28, 28, 28, 255))
        draw.ellipse(right_ear, fill=(28, 28, 28, 255))

        # Snout
        snout_w = face_radius
        snout_h = face_radius // 1.4
        snout_bbox = [cx - snout_w // 2, cy + face_radius // 8, cx + snout_w // 2, cy + face_radius // 2]
        draw.ellipse(snout_bbox, fill=(60, 60, 60, 255))

        # Nose
        nose_w = snout_w // 3
        nose_h = snout_h // 3
        nose_bbox = [cx - nose_w // 2, cy + face_radius // 8 + nose_h // 4, cx + nose_w // 2, cy + face_radius // 8 + nose_h]
        draw.ellipse(nose_bbox, fill=(10, 10, 10, 255))

        # Angry brows (sharp triangles)
        brow_offset_x = face_radius // 2
        brow_offset_y = face_radius // 2
        # Left brow
        lb = [(cx - brow_offset_x, cy - brow_offset_y // 2), (cx - brow_offset_x // 4, cy - brow_offset_y), (cx - brow_offset_x // 4 + 10, cy - brow_offset_y // 2)]
        rb = [(cx + brow_offset_x, cy - brow_offset_y // 2), (cx + brow_offset_x // 4, cy - brow_offset_y), (cx + brow_offset_x // 4 - 10, cy - brow_offset_y // 2)]
        draw.polygon(lb, fill=(20, 20, 20))
        draw.polygon(rb, fill=(20, 20, 20))

        # Eyes: neon green (left) and neon purple (right)
        eye_w = face_radius // 3
        eye_h = face_radius // 4
        left_eye_center = (cx - face_radius // 2, cy - face_radius // 8)
        right_eye_center = (cx + face_radius // 2, cy - face_radius // 8)

        # helper to draw glowing eye
        def draw_glowing_eye(center, color):
            lx, ly = center
            glow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            gdraw = ImageDraw.Draw(glow)
            max_r = eye_w
            for i in range(max_r, 0, -6):
                alpha = int(25 * (1 + (max_r - i) / max_r))
                r = int((i / max_r) * 1.0 * eye_w)
                gdraw.ellipse([lx - r, ly - r, lx + r, ly + r], fill=(color[0], color[1], color[2], alpha))
            # central pupil/iris
            gdraw.ellipse([lx - eye_w // 2, ly - eye_h // 2, lx + eye_w // 2, ly + eye_h // 2], fill=(255, 255, 255, 255))
            blurred = glow.filter(ImageFilter.GaussianBlur(radius=4))
            img.alpha_composite(blurred)

        draw_glowing_eye(left_eye_center, (0, 255, 100))   # neon green
        draw_glowing_eye(right_eye_center, (180, 0, 255))  # neon purple

        # Add subtle outline glow to face
        outline = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(outline)
        odraw.ellipse([face_bbox[0]-6, face_bbox[1]-6, face_bbox[2]+6, face_bbox[3]+6], outline=(50, 0, 80, 120), width=8)
        img = Image.alpha_composite(img, outline)

        # Optional watermark text at bottom
        try:
            font = ImageFont.load_default()
            text = "KoalaByte"
            tw, th = draw.textsize(text, font=font)
            draw.text((self.width - tw - 8, self.height - th - 8), text, fill=(120, 120, 120), font=font)
        except Exception:
            pass

        return img

    def show(self, duration: float = 2.0) -> None:
        logger.info("Showing splash screen (duration=%.1fs)", duration)
        if not PYGAME_AVAILABLE:
            # If Pillow available, still generate and save the image for boards that read assets
            if 'Image' in globals():
                try:
                    if not self.splash_path.exists():
                        img = self._generate_cyberpunk_koala()
                        img.save(self.splash_path)
                        logger.info("Generated koalabyte logo at %s", self.splash_path)
                except Exception:
                    logger.debug("Could not generate or save splash image", exc_info=True)
            time.sleep(duration)
            return

        # Ensure pygame is initialized on a display-capable system
        try:
            os.environ.setdefault("SDL_VIDEODRIVER", os.environ.get("SDL_VIDEODRIVER", "x11"))
            pygame.init()
            screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("KoalaByte")

            # Load logo image or generate one
            if self.splash_path.exists():
                img = Image.open(self.splash_path).convert("RGBA")
                img = img.resize((self.width, self.height), Image.LANCZOS)
            else:
                img = self._generate_cyberpunk_koala()
                try:
                    img.save(self.splash_path)
                    logger.info("Saved generated koalabyte logo to %s", self.splash_path)
                except Exception:
                    logger.debug("Could not save generated logo", exc_info=True)

            # Convert PIL image to pygame surface
            mode = img.mode
            size = img.size
            data = img.tobytes()
            pygame_image = pygame.image.fromstring(data, size, mode)

            clock = pygame.time.Clock()
            start = time.time()
            running = True
            while running and (time.time() - start) < duration:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                screen.blit(pygame.transform.scale(pygame_image, (self.width, self.height)), (0, 0))
                pygame.display.flip()
                clock.tick(30)

        except Exception as exc:
            logger.warning("Splash display failed: %s", exc)
            time.sleep(duration)
        finally:
            try:
                pygame.quit()
            except Exception:
                pass


class Display:
    """DS1: Generic 3.5 inch HDMI LCD, 5V, Jetson-driven display."""

    def __init__(self, component: HardwareComponent, width: int = 800, height: int = 480):
        self.component = component
        self.width = width
        self.height = height
        self.initialized = False

    def initialize(self) -> None:
        logger.info("Display initialized: %s (%sx%s target)", self.component.describe(), self.width, self.height)
        self.initialized = True


class Camera:
    """CAM1: (IMX708 CSI camera module)"""

    def __init__(self, component: HardwareComponent, csi_id: int = 0):
        self.component = component
        self.csi_id = csi_id
        self.initialized = False

    def initialize(self) -> None:
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
        """Execute device boot sequence and show splash screen before initialization."""
        logger.info("=" * 60)
        logger.info("KoalaByte v%s - BOOT SEQUENCE", self.VERSION)
        logger.info("Time: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logger.info("=" * 60)

        # Show splash screen first (best-effort)
        splash = SplashScreen(width=self.display.width, height=self.display.height)
        try:
            splash.show(duration=2.0)
        except Exception:
            logger.debug("Splash display failed or was skipped", exc_info=True)

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
            print("3) Show splash")
            print("4) Exit")
            choice = input("Select: ").strip()
            if choice == "1":
                self.battery.log_status()
            elif choice == "2":
                self.safety.acknowledge_lab_mode()
            elif choice == "3":
                splash = SplashScreen(width=self.display.width, height=self.display.height)
                splash.show(duration=2.0)
            elif choice == "4":
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
