"""KoalaByte Rev 0.5 hardware configuration.

This file is the single firmware truth source. Keep it aligned with docs/bom.yaml.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT_DIR / "assets"
DOCS_DIR = ROOT_DIR / "docs"

Color = Tuple[int, int, int]


@dataclass(frozen=True)
class DisplayConfig:
    name: str = "Generic 3.5 inch HDMI capacitive touchscreen"
    width: int = 800
    height: int = 480
    interface: str = "HDMI"
    touch_interface: str = "USB/I2C bridge, model dependent"
    splash_asset: str = "assets/koalabyte_logo.png"


@dataclass(frozen=True)
class EyeConfig:
    controller: str = "ESP32-S3-DualEye-LCD-1.28"
    uart_port: str = "/dev/ttyTHS1"
    baudrate: int = 921600
    left_theme: str = "ultraviolet"
    right_theme: str = "cyber_green"
    left_eye_display: str = "1.28 inch round LCD"
    right_eye_display: str = "1.28 inch round LCD"


@dataclass(frozen=True)
class LedConfig:
    gpio_pin: int = 7
    leds_per_eye: int = 16
    left_color: Color = (148, 0, 255)
    right_color: Color = (0, 255, 80)
    brightness: float = 0.35


@dataclass(frozen=True)
class CameraConfig:
    model: str = "IMX219"
    interface: str = "CSI-0"
    location: str = "right eye"
    default_resolution: str = "1920x1080"


@dataclass(frozen=True)
class AntennaConfig:
    wifi_internal: str = "dual internal 2.4/5 GHz antennas"
    wifi_external: str = "dual external SMA/IPEX antenna option"
    nfc: str = "left-ear internal NFC coil"
    gps: str = "active ceramic patch antenna"
    subghz: str = "CC1101 tuned antenna matched to selected band"


@dataclass(frozen=True)
class WirelessConfig:
    wifi_chipset: str = "MediaTek MT7921K"
    wifi_bus: str = "M.2 Key-E PCIe"
    internal_antennas: int = 2
    external_antennas: int = 2
    bluetooth_coprocessor: str = "nRF52840"
    bluetooth_uart: str = "/dev/ttyTHS2"
    antennas: AntennaConfig = field(default_factory=AntennaConfig)


@dataclass(frozen=True)
class ButtonConfig:
    f1: str = "ESP32-S3 UART command: F1"
    f2: str = "ESP32-S3 UART command: F2"
    f3: str = "ESP32-S3 UART command: F3"
    f4: str = "ESP32-S3 UART command: F4"
    f5: str = "ESP32-S3 UART command: F5"
    f6: str = "ESP32-S3 UART command: F6"
    nose_switch_gpio: int = 15


@dataclass(frozen=True)
class PowerConfig:
    battery_ref: str = "BAT1"
    battery: str = "2S2P 21700 Li-ion pack"
    nominal_voltage_v: float = 7.4
    full_charge_voltage_v: float = 8.4
    bms_ref: str = "BMS1"
    bms: str = "2S Li-ion BMS with balancing and overcharge protection"
    regulator_ref: str = "REG1"
    regulator: str = "5V 12A synchronous buck regulator module"
    regulator_path: str = "2S pack -> BMS -> F1 fuse -> REG1 5V system rail"
    power_input_ref: str = "J_USB"
    power_input: str = "USB-C 5V input; validate PD/current design"
    fuse_ref: str = "F1"
    fuse: str = "10A resettable fuse between BMS output and regulator"
    low_battery_percent: int = 15
    critical_battery_percent: int = 7


@dataclass(frozen=True)
class PeripheralConfig:
    pn532_i2c_bus: int = 1
    pn532_i2c_addr: str = "0x24"
    nfc_coil_location: str = "inside left ear"
    gps_port: str = "/dev/ttyTHS0"
    gps_baudrate: int = 9600
    cc1101_bus: int = 0
    cc1101_cs: int = 0
    rtl_sdr_bus: str = "USB3"
    ir_rx_gpio: int = 23
    ir_tx_gpio: int = 24
    buttons: ButtonConfig = field(default_factory=ButtonConfig)


@dataclass(frozen=True)
class SafetyConfig:
    lab_mode_required: bool = True
    safety_banner: str = (
        "KoalaByte lab mode only: use on owned systems or with explicit written authorization."
    )
    disabled_actions: tuple[str, ...] = (
        "credential_theft",
        "unauthorized_access",
        "persistence",
        "evasion",
        "destructive_actions",
    )


@dataclass(frozen=True)
class KoalaByteConfig:
    version: str = "0.5.0"
    board: str = "KoalaByte Rev 0.5 Version B"
    main_compute: str = "NVIDIA Jetson Orin Nano Super 8GB"
    display: DisplayConfig = field(default_factory=DisplayConfig)
    eyes: EyeConfig = field(default_factory=EyeConfig)
    leds: LedConfig = field(default_factory=LedConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    wireless: WirelessConfig = field(default_factory=WirelessConfig)
    peripherals: PeripheralConfig = field(default_factory=PeripheralConfig)
    power: PowerConfig = field(default_factory=PowerConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)


CONFIG = KoalaByteConfig()


def as_dict() -> Dict[str, object]:
    """Return a compact serializable config summary."""
    return {
        "version": CONFIG.version,
        "board": CONFIG.board,
        "main_compute": CONFIG.main_compute,
        "display": CONFIG.display.__dict__,
        "eyes": CONFIG.eyes.__dict__,
        "leds": CONFIG.leds.__dict__,
        "camera": CONFIG.camera.__dict__,
        "wireless": {
            **CONFIG.wireless.__dict__,
            "antennas": CONFIG.wireless.antennas.__dict__,
        },
        "peripherals": {
            **CONFIG.peripherals.__dict__,
            "buttons": CONFIG.peripherals.buttons.__dict__,
        },
        "power": CONFIG.power.__dict__,
        "safety": CONFIG.safety.__dict__,
    }
