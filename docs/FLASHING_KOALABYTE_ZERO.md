# KoalaByte Zero flashing guide

This guide is the canonical flash/deploy procedure for the KoalaByte Zero Rev 0.5 firmware tree.

## What gets flashed or installed

KoalaByte Zero has two software targets:

1. **Jetson runtime** — the Python firmware service that runs on the NVIDIA Jetson Orin Nano / Orin Nano Super.
2. **ESP32-S3 eye controller** — the optional PlatformIO firmware target for the ESP32-S3-DualEye-LCD-1.28 board, when the `esp32_mcu/` project is present.

The Jetson side is deployed like an embedded Linux firmware package. The ESP32-S3 side is flashed over USB serial.

## Safety and authorization

Use this only on hardware you own or operate with explicit authorization. Runtime mode is intentionally gated behind `KOALABYTE_LAB_MODE=1` so the device does not start active lab functions by accident.

## Hardware checklist before power-on

- Confirm the 5V regulator is rated for the expected Jetson + display + USB load.
- Confirm battery/BMS polarity, fuse placement, and rear power switch wiring before connecting the Jetson.
- Connect the 3.5 inch HDMI display and touch interface.
- Connect the ESP32-S3 dual-eye board over USB or UART.
- Connect only the peripherals needed for the first boot test.
- Leave RF transmit-capable modules disconnected until local regulations, antenna matching, and lab authorization are confirmed.

## Host PC prerequisites

Use a Linux PC, WSL, or the Jetson itself for setup.

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip build-essential
```

Optional for ESP32-S3 flashing:

```bash
python3 -m pip install --user platformio
```

## Step 1 — clone the repo

```bash
git clone https://github.com/greatwhitek9-lab/KoalaByte-Zero.git
cd KoalaByte-Zero
```

## Step 2 — create the Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## Step 3 — verify the firmware package

```bash
python3 -m koalabyte.main --print-config
python3 -m koalabyte.main --self-test
python3 -m pytest -q
```

If the repo has the deploy verification script, this is equivalent:

```bash
bash scripts/verify_deploy.sh
```

## Step 4 — install/deploy to the Jetson

Run the helper from the repo root:

```bash
chmod +x scripts/flash_koalabyte_zero.sh
./scripts/flash_koalabyte_zero.sh --install-service
```

This creates `/opt/koalabyte-zero`, installs Python dependencies into `/opt/koalabyte-zero/.venv`, runs self-tests, and installs a `koalabyte-zero.service` systemd unit.

## Step 5 — start the Jetson runtime

Manual first boot:

```bash
cd /opt/koalabyte-zero
source .venv/bin/activate
export KOALABYTE_LAB_MODE=1
python3 -m koalabyte.main --self-test
python3 -m koalabyte.main
```

Systemd service boot:

```bash
sudo systemctl daemon-reload
sudo systemctl enable koalabyte-zero.service
sudo systemctl start koalabyte-zero.service
sudo journalctl -u koalabyte-zero.service -f
```

## Step 6 — flash the ESP32-S3 eye controller, if present

Plug in the ESP32-S3-DualEye board and find the serial port:

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Flash with PlatformIO:

```bash
python3 -m pip install --user platformio
bash scripts/build_flash_esp32.sh /dev/ttyUSB0
```

Replace `/dev/ttyUSB0` with the actual port.

If `esp32_mcu/` is not present yet, the Jetson runtime can still be deployed. Add the ESP32-S3 PlatformIO project later and re-run the command above.

## Step 7 — production flash validation

Run these checks before calling a device flash-ready:

```bash
python3 -m koalabyte.main --print-config
python3 -m koalabyte.main --self-test
python3 -m pytest -q
systemctl status koalabyte-zero.service --no-pager
```

Expected result:

- Config prints without import errors.
- Self-test exits with code `0`.
- Pytest exits with code `0`.
- The systemd service starts and logs the KoalaByte boot message.

## Troubleshooting

### `ModuleNotFoundError: koalabyte`

Run from the repo root or install the package into the active virtual environment:

```bash
source .venv/bin/activate
python3 -m pip install -e .
```

### `KOALABYTE_LAB_MODE` error

Runtime mode requires explicit lab acknowledgement:

```bash
export KOALABYTE_LAB_MODE=1
```

### ESP32 upload fails

Check the USB cable supports data, confirm the port, then hold the board boot button while upload starts if the board does not auto-enter bootloader mode.

### Jetson service fails

Inspect logs:

```bash
sudo journalctl -u koalabyte-zero.service -n 100 --no-pager
```

Then rerun self-test manually from `/opt/koalabyte-zero`.
