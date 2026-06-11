# KoalaByte Firmware — Device Installation & Run Guide

## Safety

- Work only on systems you own or are explicitly authorized to test.
- Verify BMS, fuse, regulator, rear power switch, and battery wiring before powering the device.
- Follow local regulations for RF-capable peripherals.

## Hardware prerequisites

- Jetson Orin Nano Super 8GB or compatible Jetson carrier setup.
- 3.5 inch HDMI touchscreen connected to HDMI and its touch interface.
- ESP32-S3-DualEye-LCD-1.28 used as the dual-eye controller.
- IMX219/IMX708 CSI camera connected on CSI-0 and mounted centered just above the eyes and below the enlarged ears.
- Back-mounted power on/off switch wired as `SW_PWR`.
- PN532 NFC module with the coil placed inside the left ear.
- MT7921K Wi-Fi/Bluetooth module on M.2 Key-E PCIe.
- Optional connected peripherals: nRF52840, NEO-M8N GPS, RTL-SDR, CC1101, and IR RX/TX.

## Install

```bash
git clone https://github.com/greatwhitek9-lab/koalabyte-firmware.git
cd koalabyte-firmware
git checkout deployable_rev_0.5
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
- The camera is centered just above the ESP32-S3 dual-eye board and below the enlarged ears.

## Maintenance

Use feature branches and pull requests. Keep `koalabyte/config.py` aligned with `docs/bom.yaml` whenever hardware changes.
