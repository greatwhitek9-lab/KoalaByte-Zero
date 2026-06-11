# KoalaByte Firmware

Deployable firmware scaffold for **KoalaByte Rev 0.5 Version B / Koalabyte Zero**.

This branch establishes one canonical Python runtime for the Jetson side of the device, a unified hardware configuration, safety-gated startup behavior, deploy verification tests, and a normalized prototype production starter package.

## Target hardware

- Main compute: NVIDIA Jetson Orin Nano Super 8GB
- Main screen: 3.5 inch HDMI touchscreen, 800x480 target
- Eye controller: ESP32-S3-DualEye-LCD-1.28
- Eye/LED theme: left ultraviolet, right cyber green
- Camera: IMX708 on CSI-0, mounted in the nose pod / central front nose assembly between the two EYE1 round LCD displays
- Wireless: MediaTek MT7921K on M.2 Key-E PCIe or USB adapter path
- Internal USB: HUB1 powered USB 3.0 hub for SDR, Wi-Fi, debug, and USB touch expansion
- NFC: PN532 over I2C with coil inside the left ear
- GPS: u-blox NEO-M8N over UART with top/rear active GPS patch antenna
- RF: RTL-SDR, CC1101, LoRa/SX1276-SX1278, 3 default external antennas plus optional LTE fourth antenna
- IR: top-of-head/front-brow IR receiver and transmitter driven through a transistor/MOSFET stage
- Audio: SPK1 speaker/buzzer for UI sounds and alerts
- Power: 5V 10-12A main regulator path, 3.3V logic rail, and 10A-class input protection

## Production starter files

The `device build schematics/` folder contains the normalized Rev0.5 prototype production starter files:

- BOM CSV
- Pick-and-place CSV
- Drill file
- Gerber files
- KiCad project/schematic/PCB starter files
- Assembly README
- Net summary
- Mechanical starter notes
- Placement update notes

These files are prototype interface-shield/harness-board starters, not final manufacturer-verified PCB release files. Run ERC/DRC, validate connector pinouts, power integrity, thermal behavior, antenna placement, enclosure tolerances, and at least one physical test spin before production ordering.

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
