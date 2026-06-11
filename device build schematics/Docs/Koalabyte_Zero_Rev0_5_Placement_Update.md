# Koalabyte Zero Rev0.5 Placement Update

This document records the normalized repo-aligned placement truth for Koalabyte Zero Rev0.5 Version B.

## Identity

- Product display name: **Koalabyte Zero**
- Hardware baseline: **KoalaByte Rev0.5 Version B**
- Primary layout: rugged koala-style handheld with enlarged ears, 3.5 inch 800x480 HDMI touchscreen, ESP32-S3 dual-eye LCD board, right-ear microphone, left-side D-pad, right-side F buttons, rear-mounted power switch, internal modular radios, and three default external antennas.

## Front placement

- **Main display:** DS1 3.5 inch HDMI touchscreen, normalized to **800x480**, mounted in the lower front face.
- **Eye assembly:** EYE1 ESP32-S3 1.28 inch Double Eye Round LCD AIoT board mounted above the main screen and below the enlarged ears.
- **Camera:** CAM1 **IMX708 CSI** camera centered just above the eyes and below the enlarged ears.
- **D-pad:** front lower-left, matching the Version B enclosure reference.
- **Function buttons:** F1, F2, and F3 stacked vertically on the front lower-right side. J10/SW1-SW8 covers the full control group.
- **Power switch:** SW_PWR is not a front or nose button. Use SW_PWR as a rear/back-mounted physical power on/off switch or regulator-enable control.

## Ear placement

- **Left ear:** NFC coil remains internal inside the left ear.
- **Right ear:** MIC1 I2S MEMS digital microphone mounts inside the right ear behind a small acoustic port.
- **Voice path:** MIC1 feeds the KoalaByte AI pet speech-input path and KillerKoala wake-word interaction.
- **Microphone harness:** Route MIC1 through J12 / J_MIC with `3V3`, `GND`, `I2S_BCLK`, `I2S_LRCLK`, `I2S_DIN`, and `SHIELD/NC`.
- Keep the MIC1 harness away from high-current regulator/battery wiring and RF feedlines.

## Top/head placement

- **IR receiver:** IR1 in the top-of-head/front brow area behind an IR-transparent window.
- **IR transmitter:** IRTX1-3 in the top-of-head/front brow area adjacent to IR1, driven through Q1 transistor/MOSFET stage. Do not drive IR LEDs directly from MCU GPIO.

## Antenna placement

Default visual/mechanical build uses **3 external antennas**:

1. **ANT_WIFI_BT:** Wi-Fi / Bluetooth external antenna, top/rear-left or top/rear service position.
2. **ANT_LORA_SUBGHZ:** LoRa / Sub-GHz external antenna, top/rear-center or top/rear-right service position, matched to selected regional band.
3. **ANT_SDR:** SDR external antenna, right-side SMA or rear-right SMA position for RTL-SDR receive.

Optional LTE build uses **4 external antennas** only when an LTE module is installed:

4. **ANT_LTE_OPT:** cellular / 4G LTE antenna. DNP on default Koalabyte Zero build.

Non-whip antenna rules:

- **GPS:** ANT_GPS_PATCH active ceramic patch antenna on the top/rear deck with sky-facing clearance.
- **NFC:** PN532/NFC coil remains internal inside the left ear. Do not draw it as an external whip antenna.

## Power and internal modules

- **REG1:** normalized to 5V 12A main rail for Jetson + display + USB load.
- **F1:** normalized to 10A-class protection after current testing.
- **REG2:** retained as 3.3V 1A logic/sensor/audio rail.
- **HUB1:** retained as powered internal USB 3.0 hub for SDR, Wi-Fi, debug, and touch expansion.
- **SPK1:** retained as speaker/buzzer for UI sounds, alerts, and optional AI pet voice output.
- **MIC1:** right-ear microphone for voice-to-AI-pet input; validate acoustic port, enclosure damping, and wake-word capture.
