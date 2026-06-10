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

The firmware config is centralized in `koalabyte/config.py` and currently targets KoalaByte Rev 0.5 Version B, Jetson Orin Nano Super, HDMI touchscreen, ESP32-S3 eye controller, PN532 NFC in the left ear, IMX219 camera, MT7921K wireless, GPS, SDR, sub-GHz radio, and IR support shims.
