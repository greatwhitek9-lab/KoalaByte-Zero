# KoalaByte Firmware — Device Installation & Run Guide

## Safety

- Work only on systems you own or are explicitly authorized to test.
- Verify BMS, fuse, regulator, rear power switch, and battery wiring before powering the device.
- Follow local regulations for RF-capable peripherals.

## Hardware prerequisites

- Jetson Orin Nano Super 8GB or compatible Jetson carrier setup.
- 3.5 inch HDMI touchscreen connected to HDMI and its touch interface; normalized target is **800x480**.
- ESP32-S3-DualEye-LCD-1.28 used as the dual-eye controller (`EYE1`).
- The production Rev 0.5 BOM uses the onboard ESP32-S3 in `EYE1`; there is no required standalone `U2` ESP32-S3-WROOM module.
- **IMX708 CSI camera** connected on CSI-0 and mounted in the nose pod / central front nose assembly between the two EYE1 round LCD displays.
- Back-mounted power on/off switch wired as `SW_PWR`.
- 5V **10-12A** main regulator path with 10A-class input protection and a 3.3V logic rail.
- Powered internal USB 3.0 hub (`HUB1`) for SDR, Wi-Fi, debug, and USB touch expansion.
- Speaker/buzzer (`SPK1`) for UI sounds and alerts.
- PN532 NFC module with the coil placed inside the left ear.
- MT7921K Wi-Fi/Bluetooth module on M.2 Key-E PCIe or USB adapter path.
- Optional connected peripherals: nRF52840, NEO-M8N GPS, RTL-SDR, CC1101, LoRa module, and IR RX/TX.

## Install

```bash
git clone https://github.com/greatwhitek9-lab/koalabyte-firmware.git
cd koalabyte-firmware
git checkout deployable-rev-0.5
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Or run:

```bash
bash scripts/setup_jetson.sh
```

## Verify

```bash
python3 -m koalabyte.main --print-config
python3 -m koalabyte.main --self-test
python3 -m pytest -q
```

Or run:

```bash
bash scripts/verify_deploy.sh
```

## Run manually

Runtime mode requires explicit lab acknowledgement:

```bash
export KOALABYTE_LAB_MODE=1
python3 -m koalabyte.main
```

The convenience script is:

```bash
KOALABYTE_LAB_MODE=1 bash scripts/run_fw.sh
```

## systemd service example

Create `/etc/systemd/system/koalabyte.service`:

```ini
[Unit]
Description=KoalaByte Firmware
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/koalabyte-firmware
Environment=KOALABYTE_LAB_MODE=1
ExecStart=/opt/koalabyte-firmware/venv/bin/python3 -m koalabyte.main
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now koalabyte
sudo journalctl -u koalabyte -f
```

## ESP32-S3 eye controller

```bash
bash scripts/build_flash_esp32.sh /dev/ttyUSB0
```

The active ESP32 project lives in `esp32_mcu/`.

## Rev 0.5 mechanical placement notes

- The prior nose switch has been removed from Rev 0.5.
- The power on/off switch is now a back-mounted switch, referenced as `SW_PWR`.
- CAM1 is an IMX708 CSI camera mounted in the nose pod / central front nose assembly between the two EYE1 round LCD displays.
- `EYE1` is mounted above the 3.5 inch 800x480 touchscreen and below the enlarged ears.
- Default build uses 3 external antennas; LTE fourth antenna is DNP unless an LTE variant is built.

## Maintenance

Use feature branches and pull requests. Keep `koalabyte/config.py`, `docs/bom.yaml`, and `device build schematics/` aligned whenever hardware changes.
