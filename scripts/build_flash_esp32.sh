#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)/esp32_mcu"
USB_PORT="${1:-/dev/ttyUSB0}"

if ! command -v platformio >/dev/null 2>&1; then
  echo "Error: PlatformIO is not installed. Install with: python3 -m pip install platformio"
  exit 1
fi

if [ ! -d "$PROJECT_DIR" ]; then
  echo "Error: ESP32 project directory not found: $PROJECT_DIR"
  exit 1
fi

platformio run --project-dir "$PROJECT_DIR"
platformio run --project-dir "$PROJECT_DIR" --target upload --upload-port "$USB_PORT"

echo "KoalaByte ESP32-S3 eye controller upload complete."
