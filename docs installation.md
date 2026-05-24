# KoalaByte Firmware Installation Guide

## Prerequisites

- NVIDIA Jetson Orin Nano Super with 8GB RAM
- ESP32-S3-WROOM MCU module
- JetPack 5.1+ OS image
- Python 3.11 or higher
- USB-C cable for development
- Linux development machine for cross-compilation

## Step 1: Jetson Setup

### Install JetPack

```bash
# On development machine
sdkmanager --cli install --logintype devzone --product Jetson \
  --version 5.1.2 --target Jetson_Orin_Nano_Super