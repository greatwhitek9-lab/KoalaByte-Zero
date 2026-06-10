# KoalaByte Firmware

Deployable firmware scaffold for **KoalaByte Rev 0.5 Version B**.

This branch establishes one canonical Python runtime for the Jetson side of the device, a unified hardware configuration, safety-gated startup behavior, and deploy verification tests.

## Target hardware

- Main compute: NVIDIA Jetson Orin Nano Super 8GB
- Main screen: 3.5 inch HDMI touchscreen, 800x480 target
- Eye controller: ESP32-S3-DualEye-LCD-1.28
- Eye/LED theme: left ultraviolet, right cyber green
- Camera: IMX219 on CSI-0, right eye location
- Wireless: MediaTek MT7921K on M.2 Key-E PCIe
- NFC: PN532 over I2C with coil inside the left ear
- GPS: u-blox NEO-M8N over UART
- Other peripherals: nRF52840, RTL-SDR, CC1101, IR RX/TX

## Quick start

```bash
python3 -m pip install -r requirements.txt
python3 -m koalabyte.main --self-test
```

To print the resolved hardware config:

```bash
python3 -m koalabyte.main --print-config
```

To start runtime mode in an authorized lab environment:

```bash
export KOALABYTE_LAB_MODE=1
python3 -m koalabyte.main
```

## Verify deployment

```bash
bash scripts/verify_deploy.sh
```

## Safety note

KoalaByte firmware is intended for owned systems, authorized lab environments, and defensive/educational testing only. Runtime mode requires explicit lab-mode acknowledgement through `KOALABYTE_LAB_MODE=1`.
