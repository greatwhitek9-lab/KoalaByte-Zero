# KoalaByte Rev 0.5 Deployment

## Canonical entry point

Use the Python package entry point instead of older root scripts with spaces in their names:

```bash
python3 -m koalabyte.main --self-test
```

## Install on Jetson

```bash
bash scripts/setup_jetson.sh
```

## Verify

```bash
bash scripts/verify_deploy.sh
```

## Runtime mode

Runtime startup is safety-gated. Enable it only for owned or explicitly authorized lab systems:

```bash
export KOALABYTE_LAB_MODE=1
python3 -m koalabyte.main
```

## Hardware alignment

The firmware config is centralized in `koalabyte/config.py` and currently targets KoalaByte Rev 0.5 Version B / Koalabyte Zero with Jetson Orin Nano Super, 800x480 HDMI touchscreen, ESP32-S3 dual-eye LCD controller, PN532 NFC in the left ear, IMX708 nose-pod camera, MT7921K wireless, powered internal USB hub, GPS, SDR, LoRa/Sub-GHz radio coverage, IR support shims, SPK1 audio alert coverage, and a 5V 10-12A power path.

## Production starter files

The checked-in `device build schematics/` folder contains the normalized prototype production starter files: BOM CSV, pick-and-place CSV, drill, Gerber, KiCad starter files, mechanical starter notes, placement notes, and net summary. These are still prototype interface-shield files and require ERC/DRC, enclosure validation, power integrity review, thermal testing, and a physical test spin before manufacturer release.
