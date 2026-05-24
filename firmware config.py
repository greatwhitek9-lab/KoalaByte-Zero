"""KoalaByte Firmware Configuration"""

import os
from dataclasses import dataclass
from typing import Dict, List


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
    DISPLAY_WIDTH = 320
    DISPLAY_HEIGHT = 240
    DISPLAY_DPI = 140
    DISPLAY_INTERFACE = "SPI"  # or DSI
    
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
    NAME = "KORA"
    SPECIES = "Koala"
    PERSONALITY = "gruff_cyberpunk"
    
    # Leveling
    MAX_LEVEL = 100
    XP_TO_LEVEL = 1000  # Base XP per level
    XP_MULTIPLIER = 1.1  # XP requirement increases per level
    
    # Moods
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
    
    # Stat Boosts per Action
    STAT_BOOSTS = {
        "wifi_scan": {"network": 1},
        "ble_discovery": {"wireless": 1},
        "ir_transmit": {"sensor": 1},
        "nfc_clone": {"memory": 1},
        "exploit_execute": {"hacker": 5},
    }
    
    # Dialogue Banks
    DIALOGUE_IDLE = [
        "What, no targets? I could crack a bank with my eyes closed.",
        "C'mon, choom. Give me something to do.",
        "This silence is deafening. Literally.",
        "You're boring me. Find something interesting.",
    ]
    
    DIALOGUE_WIFI_SCAN = [
        "Ugh, another open network? People are idiots. Let's fry 'em.",
        "Scanning the airwaves... lots of low-hanging fruit here.",
        "WiFi signals detected. Time to have some fun.",
    ]
    
    DIALOGUE_NFC = [
        "Nice. One less fob between you and the mainframe.",
        "RFID tag cloned. You're a natural at this.",
        "Emulation active. The system thinks you own it now.",
    ]
    
    DIALOGUE_LOW_BATTERY = [
        "Wire's fraying, choom. Juice up or we're both sleeping on cold concrete.",
        "Battery critically low. Plug me in or I'm going dark.",
        "Fading... need power... now...",
    ]


@dataclass
class SecurityConfig:
    """Security and Ethical Guidelines"""
    
    # Feature Flags (disable for restricted environments)
    ENABLE_DEAUTH_ATTACKS = True
    ENABLE_PACKET_INJECTION = True
    ENABLE_RF_JAMMING = False  # Disabled by default (illegal)
    ENABLE_EXPLOIT_PAYLOADS = True
    
    # Logging
    LOG_ALL_ACTIONS = True
    LOG_FILE_PATH = "/var/log/koalabyte/pentest.log"
    LOG_SENSITIVE_DATA = False  # Disable logging of credentials
    
    # Rate Limiting
    DEAUTH_PACKET_LIMIT_PER_MINUTE = 50
    PROBE_REQUEST_LIMIT_PER_MINUTE = 100
    
    # Targeting Restrictions
    BLACKLIST_NETWORKS = [
        "FBI-Guest",
        "Police-Network",
        "Military",
    ]
    WHITELIST_MODE = False  # If True, only scan whitelisted networks
    
    # Warnings
    SHOW_ETHICAL_WARNINGS = True
    REQUIRE_CONFIRMATION_FOR_ATTACKS = True


@dataclass
class NetworkConfig:
    """Network Interface Configuration"""
    
    # WiFi
    WIFI_INTERFACE = "wlan0"
    WIFI_MONITOR_MODE = "wlan0mon"
    WIFI_CHANNELS_2GHZ = list(range(1, 14))  # 1-13
    WIFI_CHANNELS_5GHZ = [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 149, 153, 157, 161, 165]
    
    # Bluetooth
    BLE_SCAN_DURATION_SECONDS = 10
    BLE_ADVERTISEMENT_CHANNELS = [37, 38, 39]
    
    # IR
    IR_FREQUENCY_KHZ = 38
    IR_CARRIER_DUTY = 50
    
    # NFC
    NFC_FREQUENCY_MHZ = 13.56
    NFC_ISO14443A_BITRATE = 106000


@dataclass
class UIConfig:
    """User Interface Configuration"""
    
    # Theme
    PRIMARY_COLOR = (128, 0, 255)  # Purple
    SECONDARY_COLOR = (0, 255, 0)  # Green
    ACCENT_COLOR = (255, 0, 255)   # Magenta
    BACKGROUND_COLOR = (10, 10, 20)  # Dark navy
    TEXT_COLOR = (200, 255, 200)  # Light green
    
    # Fonts
    FONT_TITLE = "fonts/courier_bold.ttf"
    FONT_BODY = "fonts/courier.ttf"
    FONT_MONO = "fonts/courier_mono.ttf"
    
    # Menu
    MENU_TIMEOUT_SECONDS = 60
    MENU_SCROLL_SPEED = 3  # Lines per scroll event
    
    # Animation
    ANIMATION_FPS = 30
    CYBERPET_SPRITE_SCALE = 2


def get_hardware_config() -> HardwareConfig:
    """Get hardware configuration"""
    return HardwareConfig()


def get_cyberpet_config() -> CyberpetConfig:
    """Get cyberpet configuration"""
    return CyberpetConfig()


def get_security_config() -> SecurityConfig:
    """Get security configuration"""
    return SecurityConfig()


def get_network_config() -> NetworkConfig:
    """Get network configuration"""
    return NetworkConfig()


def get_ui_config() -> UIConfig:
    """Get UI configuration"""
    return UIConfig()
