"""KoalaByte Zero Rev 0.5 hardware configuration.

This file is the single firmware truth source. Keep it aligned with docs/bom.yaml,
docs/koalabyte_zero_placement_update.md, and the checked-in
``device build schematics`` production starter package.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT_DIR / "assets"
DOCS_DIR = ROOT_DIR / "docs"
DEVICE_BUILD_SCHEMATICS_DIR = ROOT_DIR / "device build schematics"

Color = Tuple[int, int, int]
DUAL_EYE_BOARD = "ESP32-S3 1.28inch Double Eye Round LCD AIoT Development Board, Onboard Dual 1.28inch IPS Displays"


@dataclass(frozen=True)
class DisplayConfig:
    ref: str = "DS1"
    name: str = "Generic 3.5 inch HDMI capacitive touchscreen"
    width: int = 800
    height: int = 480
    interface: str = "HDMI"
    touch_interface: str = "USB/I2C bridge, model dependent"
    splash_asset: str = "assets/koalabyte_zero_logo.png"


@dataclass(frozen=True)
class EyeConfig:
    ref: str = "EYE1"
    controller: str = DUAL_EYE_BOARD
    uart_port: str = "/dev/ttyTHS1"
    baudrate: int = 921600
    interface: str = "USB/UART"
    mount_location: str = "front face, above 3.5 inch touch screen and below enlarged ears"
    left_theme: str = "ultraviolet"
    right_theme: str = "cyber_green"
    left_eye_display: str = "1.28 inch round IPS LCD"
    right_eye_display: str = "1.28 inch round IPS LCD"


@dataclass(frozen=True)
class EyeDisplayConfig:
    """Display behavior for the ESP32-S3 dual-eye LCD board."""

    board_ref: str = "EYE1"
    board: str = DUAL_EYE_BOARD
    left_color: Color = (148, 0, 255)
    right_color: Color = (0, 255, 80)
    brightness: float = 0.35
    legacy_ws2812_eye_rings: bool = False


@dataclass(frozen=True)
class CameraConfig:
    ref: str = "CAM1"
    model: str = "IMX708"
    interface: str = "CSI-0"
    location: str = "centered just above eyes and below ears"
    default_resolution: str = "4608x2592"


@dataclass(frozen=True)
class AntennaConfig:
    default_external_count: int = 3
    optional_lte_external_count: int = 4
    wifi_bt_ref: str = "ANT_WIFI_BT"
    lora_subghz_ref: str = "ANT_LORA_SUBGHZ"
    sdr_ref: str = "ANT_SDR"
    optional_lte_ref: str = "ANT_LTE_OPT"
    gps_patch_ref: str = "ANT_GPS_PATCH"
    wifi_bt_external: str = "top/rear-left external WiFi/Bluetooth antenna, 2.4/5 GHz, IPEX/SMA feed"
    lora_subghz_external: str = "top/rear LoRa/Sub-GHz external antenna matched to selected 868/915 MHz or regional band"
    sdr_external: str = "right-side or rear-right SMA external SDR antenna for RTL-SDR receive"
    optional_lte_external: str = "optional cellular / 4G LTE external antenna; install only for LTE build"
    nfc: str = "left-ear internal NFC coil; not an external whip antenna"
    gps: str = "active ceramic patch antenna on top/rear deck with sky-facing clearance"


@dataclass(frozen=True)
class WirelessConfig:
    ref: str = "WIFI1"
    wifi_chipset: str = "MediaTek MT7921K"
    wifi_bus: str = "M.2 Key-E PCIe or USB adapter"
    internal_antennas: int = 2
    default_external_antennas: int = 3
    optional_lte_external_antennas: int = 4
    bluetooth_coprocessor: str = "nRF52840"
    bluetooth_uart: str = "/dev/ttyTHS2"
    antennas: AntennaConfig = field(default_factory=AntennaConfig)


@dataclass(frozen=True)
class UsbConfig:
    hub_ref: str = "HUB1"
    hub: str = "Mini internal powered USB 3.0 hub"
    purpose: str = "internal expansion for SDR, Wi-Fi, debug, and USB touch"
    powered_preferred: bool = True


@dataclass(frozen=True)
class AudioConfig:
    speaker_ref: str = "SPK1"
    speaker: str = "8 Ohm mini speaker / piezo buzzer"
    microphone_ref: str = "MIC1"
    microphone: str = "I2S MEMS digital microphone module"
    microphone_interface: str = "I2S or USB audio adapter"
    microphone_location: str = "inside right ear"
    microphone_purpose: str = "speech input for KoalaByte AI pet voice interaction"
    purpose: str = "UI sounds, alerts, and voice interaction"
    optional_amp_recommended: bool = True


@dataclass(frozen=True)
class ButtonConfig:
    connector_ref: str = "J10"
    switch_refs: str = "SW1-SW8"
    f1: str = "front lower-right vertical stack: ESP32-S3 UART command F1"
    f2: str = "front lower-right vertical stack: ESP32-S3 UART command F2"
    f3: str = "front lower-right vertical stack: ESP32-S3 UART command F3"
    f4: str = "reserved rear/side service command F4"
    f5: str = "reserved rear/side service command F5"
    f6: str = "reserved rear/side service command F6"
    dpad: str = "front lower-left D-pad"
    select: str = "front/menu select button"
    back: str = "front/menu back button"
    rear_power_switch: str = "SW_PWR rear/back-mounted physical power on/off switch"


@dataclass(frozen=True)
class PowerConfig:
    battery_ref: str = "PWR1/BAT1"
    battery: str = "USB-C PD power bank / 2S Li-ion pack prototype supply (2S2P 21700 pack)"
    nominal_voltage_v: float = 7.4
    full_charge_voltage_v: float = 8.4
    bms_ref: str = "BMS1"
    bms: str = "2S Li-ion BMS with balancing and overcharge protection"
    charger_ref: str = "J_CHG"
    charger: str = "2S Li-ion charger input, 8.4V CC/CV, 2A-4A target"
    charger_notes: str = "Charging input must be isolated from live system rail or power-path regulation"
    regulator_ref: str = "REG1"
    regulator: str = "5V 10-12A synchronous buck regulator module"
    regulator_min_current_a: int = 10
    regulator_preferred_current_a: int = 12
    regulator_path: str = "PWR1/BAT1 2S pack -> BMS1 -> F1 fuse -> rear switch SW_PWR -> REG1 5V system rail"
    logic_regulator_ref: str = "REG2"
    logic_regulator: str = "3.3V 1A regulator for sensors and logic rail"
    power_input_ref: str = "J_USB/J11"
    power_input: str = "USB-C power input / 5V main input; validate PD/current design"
    fuse_ref: str = "F1"
    fuse: str = "10A resettable fuse or replaceable blade fuse between BMS output and regulator"
    power_switch_ref: str = "SW_PWR"
    power_switch_location: str = "back of device"
    low_battery_percent: int = 15
    critical_battery_percent: int = 7


@dataclass(frozen=True)
class PeripheralConfig:
    nfc_ref: str = "NFC1"
    pn532_i2c_bus: int = 1
    pn532_i2c_addr: str = "0x24"
    nfc_coil_location: str = "inside left ear"
    gps_ref: str = "GPS1"
    gps_port: str = "/dev/ttyTHS0"
    gps_baudrate: int = 9600
    gps_antenna_location: str = "top/rear active ceramic patch, sky-facing"
    subghz_ref: str = "RF1"
    cc1101_bus: int = 0
    cc1101_cs: int = 0
    lora_ref: str = "LORA1"
    lora_bus: int = 0
    lora_cs: int = 1
    rtl_sdr_ref: str = "SDR1"
    rtl_sdr_bus: str = "USB3"
    ir_rx_ref: str = "IR1"
    ir_tx_ref: str = "IRTX1-3"
    ir_driver_ref: str = "Q1"
    ir_rx_gpio: int = 23
    ir_tx_gpio: int = 24
    ir_rx_location: str = "top-of-head/front brow IR-transparent window"
    ir_tx_location: str = "top-of-head/front brow IR-transparent window adjacent to IR receiver"
    buttons: ButtonConfig = field(default_factory=ButtonConfig)


@dataclass(frozen=True)
class SafetyConfig:
    lab_mode_required: bool = True
    safety_banner: str = (
        "KoalaByte lab mode only: use on owned systems or with explicit written authorization."
    )
    disabled_actions: tuple[str, ...] = (
        "outside_authorized_lab",
        "missing_owner_permission",
        "unsafe_operation",
        "destructive_operation",
    )


@dataclass(frozen=True)
class KoalaByteConfig:
    version: str = "0.5.1"
    product_name: str = "KoalaByte Zero"
    board: str = "KoalaByte Zero Rev 0.5 Version B"
    main_compute: str = "NVIDIA Jetson Orin Nano Super 8GB"
    production_folder: str = "device build schematics"
    display: DisplayConfig = field(default_factory=DisplayConfig)
    eyes: EyeConfig = field(default_factory=EyeConfig)
    eye_display: EyeDisplayConfig = field(default_factory=EyeDisplayConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    wireless: WirelessConfig = field(default_factory=WirelessConfig)
    usb: UsbConfig = field(default_factory=UsbConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    peripherals: PeripheralConfig = field(default_factory=PeripheralConfig)
    power: PowerConfig = field(default_factory=PowerConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)


CONFIG = KoalaByteConfig()


def as_dict() -> Dict[str, object]:
    """Return a compact serializable config summary."""
    return {
        "version": CONFIG.version,
        "product_name": CONFIG.product_name,
        "board": CONFIG.board,
        "main_compute": CONFIG.main_compute,
        "production_folder": CONFIG.production_folder,
        "display": CONFIG.display.__dict__,
        "eyes": CONFIG.eyes.__dict__,
        "eye_display": CONFIG.eye_display.__dict__,
        "leds": CONFIG.eye_display.__dict__,
        "camera": CONFIG.camera.__dict__,
        "wireless": {
            **CONFIG.wireless.__dict__,
            "antennas": CONFIG.wireless.antennas.__dict__,
        },
        "usb": CONFIG.usb.__dict__,
        "audio": CONFIG.audio.__dict__,
        "peripherals": {
            **CONFIG.peripherals.__dict__,
            "buttons": CONFIG.peripherals.buttons.__dict__,
        },
        "power": CONFIG.power.__dict__,
        "safety": CONFIG.safety.__dict__,
    }
