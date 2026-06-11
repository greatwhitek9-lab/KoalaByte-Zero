# KoalaByte Rev0.5 Version B Prototype Production Starter Package

Package normalized for repo alignment on 2026-06-11.

## What this package is

This is a **Rev0.5 prototype starter package** for the Koalabyte Zero Version B layout: Jetson Orin Nano Super, 3.5 inch HDMI touchscreen, ESP32-S3 dual 1.28 inch round LCD eye board, modular radios, and a serviceable internal harness/interface shield.

It includes:

- BOM CSV
- Pick-and-place CSV for the interface shield
- Excellon drill file
- Gerber starter set
- KiCad project, schematic, and PCB starter files
- Net summary and assembly notes
- Mechanical starter notes

## Normalized mismatch fixes

1. DS1 display is normalized to **3.5 inch HDMI touchscreen, 800x480, 5V**.
2. CAM1 camera is normalized to **IMX708 CSI** and placed in the nose pod / central front nose assembly.
3. REG1 power is upgraded to **5V 10-12A**.
4. F1 protection is upgraded to **10A-class input protection**.
5. SW_PWR is corrected as a rear/back-mounted power switch and is not a malformed BOM/PnP row.
6. HUB1 powered internal USB 3.0 hub is retained.
7. SPK1 speaker/buzzer UI alert component is retained.
8. J10/SW1-SW8, antennas, IR RX/TX, NFC left-ear coil, GPS patch, and optional LTE DNP rules are aligned with repo config.

## Critical limitation

This is **not a final verified production-ready design**. A final manufacturer-ready package still requires:

- exact enclosure dimensions
- confirmed 3.5 inch HDMI LCD model and mounting pattern
- exact Jetson dev kit carrier dimensions and connector clearances
- exact ESP32-S3 dual-eye board dimensions, cable orientation, and power/control wiring
- validated connector pinout mapping
- ERC/DRC in KiCad
- power integrity review
- thermal testing with Jetson load
- antenna placement review
- battery/BMS safety review
- at least one physical test build and revision

## Recommended manufacturer note

Order as a **prototype interface shield / harness board**, not as a complete KoalaByte mainboard. The Jetson, display, USB hub, SDR, Wi-Fi, GPS, NFC, LoRa/CC1101, EYE1 dual-eye LCD board, battery/power modules, and antennas remain mounted as off-the-shelf modules inside the 3D printed enclosure.

## Assembly sequence

1. Print or mock up the Version B clamshell enclosure.
2. Mount the 3.5 inch 800x480 HDMI LCD to the front plate.
3. Mount the Jetson Orin Nano Super dev kit on standoffs with active cooling and airflow gap.
4. Mount the KoalaByte interface shield behind or below the Jetson, keeping service access to headers.
5. Install EYE1 above the 3.5 inch touchscreen and below the enlarged ears.
6. Install CAM1 IMX708 into the nose pod / central front nose assembly.
7. Install PN532/NFC coil inside the left ear.
8. Install GPS, LoRa, CC1101, RTL-SDR, IR RX/TX, buttons, and rear SW_PWR using locking connectors where possible.
9. Install HUB1 internal USB hub and connect SDR/Wi-Fi/debug/touch peripherals.
10. Install REG1 5V 10-12A power path, REG2 3.3V logic rail, F1 10A-class protection, and battery/power module.
11. Confirm continuity and polarity before powering the Jetson.
12. Run firmware self-test and thermal/load testing before enclosure closure.
