"""KoalaByte Firmware Configuration"""

import os
from dataclasses import dataclass
from typing import Dict, List

# Constants for defaults and reusability
DEFAULT_UI_COLORS = {
    "PRIMARY": (128, 0, 255),
    "SECONDARY": (0, 255, 0),
    "ACCENT": (255, 0, 255),
    "BACKGROUND": (10, 10, 20),
    "TEXT": (200, 255, 200),
}

@dataclass
class HardwareConfig:
    """Hardware specifications for KoalaByte v2.0"""

    # Compute
    JETSON_MODEL = "Orin Nano Super"
    JETSON_RAM_GB = 8
    JETSON_STORAGE_GB = 64

    # MCU
    ESP32_VARIANT = "ESP32-S3-WROOM-1-N8R8"
    UART_BAUDRATE = 115200

    # Display
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 480
    DISPLAY_DPI = 140
    DISPLAY_INTERFACE = "HDMI"  # Matched with main code

    # Camera
    CAMERA_RESOLUTION = (1920, 1080)
    CAMERA_FPS = 30
    CAMERA_MODULE = "IMX219"  # Right eye

    # LED Rings
    LED_COUNT_PER_RING = 24
    LED_LEFT_COLOR = (128, 0, 255)  # Purple
    LED_RIGHT_COLOR = (0, 255, 0)   # Green
    LED_NOSE_COLOR = (255, 255, 255)  # White

    # Battery
    BATTERY_CAPACITY_MAH = 10000
    BATTERY_VOLTAGE_NOMINAL = 7.4  # 2S Li-ion
    BATTERY_FAST_CHARGE_MA = 2000

    # Thermal
    THERMAL_WARNING_CELSIUS = 70
    THERMAL_THROTTLE_CELSIUS = 80
    THERMAL_SHUTDOWN_CELSIUS = 90
    FAN_PWM_MIN = 30
    FAN_PWM_MAX = 100

    # Buttons
    BUTTON_LAYOUT = {
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
    """AI Cyberpet Configuration"""

    # Identity
    NAME = "KillerKoala"
    SPECIES = "Koala"
    PERSONALITY = "gruff_cyberpunk"

    # Leveling
    MAX_LEVEL = 100
    XP_TO_LEVEL = 1000  # Base XP per level
    XP_MULTIPLIER = 1.1  # XP requirement increases per level

    # Moods (extended alignment with main code personalities)
    MOODS = {
        "idle": {"color": (100, 100, 100), "description": "Waiting for action"},
        "active": {"color": (200, 200, 0), "description": "Executing scan"},
        "hungry": {"color": (255, 100, 0), "description": "Battery low"},
        "aggressive": {"color": (255, 0, 0), "description": "Attack mode"},
        "legendary": {"color": (255, 0, 255), "description": "Elite status"},
    }

    # Personality Tiers
    PERSONALITY_TIERS = {
        "kid": (1, 10),
        "hacker": (11, 25),
        "elite": (26, 50),
        "legend": (51, 100),
    }

    # XP Rewards
    XP_REWARDS = {
        "wifi_scan": 10,
        "ble_discovery": 15,
        "ir_transmit": 8,
        "nfc_clone": 20,
        "exploit_execute": 50,
        "new_target_type": 100,
    }

    # Dialogue Banks
    DIALOGUE_IDLE = [
        "What, no targets? I could crack a bank with my eyes closed.",
        "C'mon, choom. Give me something to do.",
    ]
    
    DIALOGUE_WIFI_SCAN = [
        "WiFi signals detected. Time to "
    ]

@dataclass
class SecurityConfig:
    pass  