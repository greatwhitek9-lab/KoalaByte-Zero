# KoalaByte Zero Rev0.5 Placement Update

This document records the current visual/mechanical placement rules for KoalaByte Rev0.5 after the rename to **Koalabyte Zero**.

## Identity

- Product display name: **Koalabyte Zero**
- Hardware baseline: KoalaByte Rev0.5 Version B
- Primary layout reference: rugged koala-style handheld with enlarged ears, 3.5 inch HDMI touchscreen, ESP32-S3 dual-eye LCD board, left-side D-pad, right-side F buttons, rear-mounted power switch, and modular internal radios.

## Front placement

- **Main display:** 3.5 inch HDMI touchscreen in the lower front face.
- **Eye assembly:** EYE1 ESP32-S3 1.28 inch Double Eye Round LCD AIoT board mounted above the main screen and below the ears.
- **Camera:** moved into the central nose pod/front nose assembly between the two round eye displays. This replaces the earlier top-brow/right-eye placement concept.
- **D-pad:** front lower-left, matching the Version B enclosure reference.
- **Function buttons:** F1, F2, and F3 are stacked vertically on the front lower-right side.
- **Power switch:** not a front button. Use SW_PWR as a rear/back-mounted physical power on/off switch.

## Top/head placement

- **IR receiver:** top-of-head/front brow area, behind an IR-transparent window.
- **IR transmitter:** top-of-head/front brow area, adjacent to the receiver, using a transistor/MOSFET driver; do not drive the IR LED directly from MCU GPIO.

## Antenna placement

Default visual/mechanical build uses **3 external antennas**:

1. **WiFi / Bluetooth external antenna** — top/rear-left or top/rear service position, using the WiFi/BT radio feed.
2. **LoRa / Sub-GHz external antenna** — top/rear-center or top/rear-right service position, matched to the selected LoRa/Sub-GHz frequency.
3. **SDR external antenna** — right-side SMA or rear-right SMA position for RTL-SDR receive.

Optional LTE build uses **4 external antennas**:

4. **Cellular / 4G LTE antenna** — only installed if an LTE module is included.

Non-whip antenna rules:

- **GPS:** active ceramic patch antenna, mounted on the top/rear deck with sky-facing clearance.
- **NFC:** internal left-ear coil. Do not draw it as an external whip antenna.

## Notes for renders and production artwork

- Every angle should show the same physical truth: 3 external antennas by default, rear-mounted power switch, camera in the nose, and IR RX/TX on top of the head.
- Optional LTE may be shown only as a callout or separate LTE variant, not installed on the default unit.
