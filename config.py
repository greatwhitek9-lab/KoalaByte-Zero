"""KoalaByte configuration.

This file provides get_hardware_config, get_cyberpet_config, get_security_config, get_ui_config
and is intentionally aligned with the original firmware config. Per request, the cyberpet XP rewards
include the previously-present action entries.
"""
from dataclasses import dataclass

@dataclass
class HardwareConfig:
    JETSON_MODEL: str = "Orin Nano Super"
    JETSON_RAM_GB: int = 8
    JETSON_STORAGE_GB: int = 64

    ESP32_VARIANT: str = "ESP32-S3-WROOM-1-N8R8"
    UART_BAUDRATE: int = 115200

    DISPLAY_WIDTH: int = 800
    DISPLAY_HEIGHT: int = 480
    DISPLAY_DPI: int = 140
    DISPLAY_INTERFACE: str = "HDMI"

    CAMERA_RESOLUTION: tuple = (1920, 1080)
    CAMERA_FPS: int = 30
    CAMERA_MODULE: str = "IMX219"

    LED_COUNT_PER_RING: int = 24
    LED_LEFT_COLOR: tuple = (128, 0, 255)
    LED_RIGHT_COLOR: tuple = (0, 255, 0)
    LED_NOSE_COLOR: tuple = (255, 255, 255)

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
                "F5": {"function": "Attack Mode", "gpio": 24},
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
                "aggressive": {"color": (255, 0, 0), "description": "Attack mode"},
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
            # Restored original action rewards per user request
            self.XP_REWARDS = {
                "wifi_scan": 10,
                "ble_discovery": 15,
                "ir_transmit": 8,
                "nfc_clone": 20,
                "exploit_execute": 50,
                "new_target_type": 100,
            }
        if self.DIALOGUE_IDLE is None:
            self.DIALOGUE_IDLE = [
                "What, no targets? I could crack a bank with my eyes closed.",
                "C'mon, choom. Give me something to do.",
            ]
        if self.DIALOGUE_WIFI_SCAN is None:
            self.DIALOGUE_WIFI_SCAN = [
                "WiFi signals detected. Time to "
            ]


@dataclass
class SecurityConfig:
    LAB_MODE_REQUIRED: bool = True
    ALLOW_OFFENSIVE_TOOLS: bool = True


@dataclass
class UIConfig:
    primary_color: tuple = (128, 0, 255)
    secondary_color: tuple = (0, 255, 0)
    accent_color: tuple = (255, 0, 255)
    background_color: tuple = (10, 10, 20)
    text_color: tuple = (200, 255, 200)


# Getter functions used by firmware.py

def get_hardware_config() -> HardwareConfig:
    return HardwareConfig()


def get_cyberpet_config() -> CyberpetConfig:
    return CyberpetConfig()


def get_security_config() -> SecurityConfig:
    return SecurityConfig()


def get_ui_config() -> UIConfig:
    return UIConfig()
