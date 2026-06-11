"""Legacy compatibility configuration for older KoalaByte scripts.

Canonical runtime configuration lives in koalabyte/config.py. This module is kept only
for older files that import get_hardware_config(), get_cyberpet_config(),
get_security_config(), or get_ui_config().
"""
from dataclasses import dataclass

DUAL_EYE_BOARD = "ESP32-S3 1.28inch Double Eye Round LCD AIoT Development Board, Onboard Dual 1.28inch IPS Displays"


@dataclass
class HardwareConfig:
    JETSON_MODEL: str = "Orin Nano Super"
    JETSON_RAM_GB: int = 8
    JETSON_STORAGE_GB: int = 64

    ESP32_VARIANT: str = "ESP32-S3"
    EYE_BOARD_REF: str = "EYE1"
    EYE_BOARD_MODULE: str = DUAL_EYE_BOARD
    EYE_BOARD_INTERFACE: str = "USB/UART"
    UART_BAUDRATE: int = 921600

    DISPLAY_WIDTH: int = 800
    DISPLAY_HEIGHT: int = 480
    DISPLAY_DPI: int = 140
    DISPLAY_INTERFACE: str = "HDMI"

    EYE_DISPLAY_DIAMETER_IN: float = 1.28
    EYE_DISPLAY_TYPE: str = "Dual round IPS LCD"
    EYE_LEFT_THEME: str = "ultraviolet"
    EYE_RIGHT_THEME: str = "cyber_green"
    LEGACY_WS2812_EYE_RINGS: bool = False

    CAMERA_RESOLUTION: tuple = (1920, 1080)
    CAMERA_FPS: int = 30
    CAMERA_MODULE: str = "IMX219"

    BATTERY_CAPACITY_MAH: int = 10000
    BATTERY_VOLTAGE_NOMINAL: float = 7.4
    BATTERY_FAST_CHARGE_MA: int = 2000

    THERMAL_WARNING_CELSIUS: int = 70
    THERMAL_THROTTLE_CELSIUS: int = 80
    THERMAL_SHUTDOWN_CELSIUS: int = 90
    FAN_PWM_MIN: int = 30
    FAN_PWM_MAX: int = 100

    BUTTON_LAYOUT: dict = None

    def __post_init__(self):
        if self.BUTTON_LAYOUT is None:
            self.BUTTON_LAYOUT = {
                "F1": {"function": "WiFi Scanner", "gpio": 17},
                "F2": {"function": "BLE Discovery", "gpio": 27},
                "F3": {"function": "IR Learn/Transmit", "gpio": 22},
                "F4": {"function": "NFC/RFID", "gpio": 23},
                "F5": {"function": "Lab Tools", "gpio": 24},
                "F6": {"function": "Settings", "gpio": 25},
                "POWER": {"function": "Power Toggle", "gpio": 4},
            }


@dataclass
class CyberpetConfig:
    NAME: str = "KillerKoala"
    SPECIES: str = "Koala"
    PERSONALITY: str = "gruff_cyberpunk"

    MAX_LEVEL: int = 100
    XP_TO_LEVEL: int = 1000
    XP_MULTIPLIER: float = 1.1

    MOODS: dict = None
    PERSONALITY_TIERS: dict = None
    XP_REWARDS: dict = None
    DIALOGUE_IDLE: list = None
    DIALOGUE_WIFI_SCAN: list = None

    def __post_init__(self):
        if self.MOODS is None:
            self.MOODS = {
                "idle": {"color": (100, 100, 100), "description": "Waiting for action"},
                "active": {"color": (200, 200, 0), "description": "Executing scan"},
                "hungry": {"color": (255, 100, 0), "description": "Battery low"},
                "legendary": {"color": (255, 0, 255), "description": "Elite status"},
            }
        if self.PERSONALITY_TIERS is None:
            self.PERSONALITY_TIERS = {
                "kid": (1, 10),
                "hacker": (11, 25),
                "elite": (26, 50),
                "legend": (51, 100),
            }
        if self.XP_REWARDS is None:
            self.XP_REWARDS = {
                "wifi_scan": 10,
                "ble_discovery": 15,
                "ir_transmit": 8,
                "nfc_read": 20,
                "new_target_type": 100,
            }
        if self.DIALOGUE_IDLE is None:
            self.DIALOGUE_IDLE = [
                "KoalaByte idle. Waiting on an authorized lab task.",
                "Dual eyes online. Systems green.",
            ]
        if self.DIALOGUE_WIFI_SCAN is None:
            self.DIALOGUE_WIFI_SCAN = [
                "WiFi signals detected. Passive lab scan ready."
            ]


@dataclass
class SecurityConfig:
    LAB_MODE_REQUIRED: bool = True
    ALLOW_OFFENSIVE_TOOLS: bool = False


@dataclass
class UIConfig:
    primary_color: tuple = (128, 0, 255)
    secondary_color: tuple = (0, 255, 0)
    accent_color: tuple = (255, 0, 255)
    background_color: tuple = (10, 10, 20)
    text_color: tuple = (200, 255, 200)


def get_hardware_config() -> HardwareConfig:
    return HardwareConfig()


def get_cyberpet_config() -> CyberpetConfig:
    return CyberpetConfig()


def get_security_config() -> SecurityConfig:
    return SecurityConfig()


def get_ui_config() -> UIConfig:
    return UIConfig()
