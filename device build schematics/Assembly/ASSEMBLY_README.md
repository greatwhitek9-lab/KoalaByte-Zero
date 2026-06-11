# KoalaByte Rev0.5 Version B Prototype Production Starter Package

Package normalized for repo alignment on 2026-06-11.

## What this package is

This is a **Rev0.5 prototype starter package** for the Koalabyte Zero Version B layout: Jetson Orin Nano Super, 3.5 inch HDMI touchscreen, ESP32-S3 dual 1.28 inch round LCD eye board, modular radios, and a serviceable internal harness/interface shield.

It includes BOM CSV, pick-and-place CSV, Excellon drill file, Gerber starter set, KiCad project/schematic/PCB starter files, net summary, assembly notes, and mechanical starter notes.

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

This is **not a final verified production-ready design**. A final manufacturer-ready package still requires exact enclosure dimensions, confirmed display and Jetson mechanical models, exact EYE1 board dimensions, validated connector pinout mapping, ERC/DRC in KiCad, power integrity review, thermal testing, antenna placement review, battery/BMS safety review, and at least one physical test build and revision.

## Recommended manufacturer note

Order as a **prototype interface shield / harness board**, not as a complete KoalaByte mainboard. The Jetson, display, USB hub, SDR, Wi-Fi, GPS, NFC, LoRa/CC1101, EYE1 dual-eye LCD board, battery/power modules, and antennas remain mounted as off-the-shelf modules inside the 3D printed enclosure.
