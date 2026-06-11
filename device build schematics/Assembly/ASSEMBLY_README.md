# KoalaByte Rev0.5 Version B Prototype Production Starter Package

Package normalized for repo alignment on 2026-06-11.

## What this package is

This is a **Rev0.5 prototype starter package** for the Koalabyte Zero Version B layout: Jetson Orin Nano Super, 3.5 inch HDMI touchscreen, ESP32-S3 dual 1.28 inch round LCD eye board, right-ear microphone, modular radios, and a serviceable internal harness/interface shield.

It includes BOM CSV, pick-and-place CSV, Excellon drill file, Gerber starter set, KiCad project/schematic/PCB starter files, net summary, assembly notes, and mechanical starter notes.

## Normalized mismatch fixes and additions

1. DS1 display is normalized to **3.5 inch HDMI touchscreen, 800x480, 5V**.
2. CAM1 camera is normalized to **IMX708 CSI** and centered just above the eyes and below the enlarged ears.
3. MIC1 is added as a **right-ear I2S MEMS digital microphone** for voice-to-AI-pet interaction.
4. J12 / J_MIC is added as the **right-ear microphone harness**.
5. MIC1 supports speech input for the **KillerKoala** wake word and KoalaByte AI pet command/answer flow.
6. REG1 power is upgraded to **5V 12A**.
7. F1 protection is upgraded to **10A-class input protection**.
8. SW_PWR is corrected as a rear/back-mounted power switch and is not a malformed BOM/PnP row.
9. HUB1 powered internal USB 3.0 hub is retained.
10. SPK1 speaker/buzzer UI alert component is retained and may be used for AI pet voice response output through an optional audio amp.
11. J10/SW1-SW8, antennas, IR RX/TX, NFC left-ear coil, GPS patch, and optional LTE DNP rules are aligned with repo config.

## MIC1 right-ear microphone assembly notes

- Mount MIC1 inside the **right ear** behind a small acoustic port.
- Do not seal the port with paint, thick adhesive, or gasket material.
- Route MIC1 to J12 / J_MIC using short twisted or shielded wiring where practical.
- J12 / J_MIC pin intent: `3V3`, `GND`, `I2S_BCLK`, `I2S_LRCLK`, `I2S_DIN`, `SHIELD/NC`.
- Keep microphone wiring away from the 5V high-current rail, REG1, battery/BMS wiring, and RF antenna feedlines.
- Validate audio capture, wake-word sensitivity, and false-trigger behavior after enclosure assembly.

## Critical limitation

This is **not a final verified production-ready design**. A final manufacturer-ready package still requires exact enclosure dimensions, confirmed display and Jetson mechanical models, exact EYE1 board dimensions, validated connector pinout mapping, ERC/DRC in KiCad, power integrity review, thermal testing, antenna placement review, battery/BMS safety review, microphone acoustic-port validation, audio noise testing, and at least one physical test build and revision.

## Recommended manufacturer note

Order as a **prototype interface shield / harness board**, not as a complete KoalaByte mainboard. The Jetson, display, USB hub, SDR, Wi-Fi, GPS, NFC, LoRa/CC1101, EYE1 dual-eye LCD board, MIC1 microphone, battery/power modules, and antennas remain mounted as off-the-shelf modules inside the 3D printed enclosure.
