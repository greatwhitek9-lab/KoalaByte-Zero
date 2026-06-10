#!/usr/bin/env bash
set -euo pipefail

cat <<'MSG'
KoalaByte Rev 0.5 host check

This script no longer unloads Broadcom modules or edits Raspberry Pi config files.
The Rev 0.5 target uses Jetson Orin Nano Super with MT7921K wireless.

Recommended checks:
  lspci | grep -i mediatek
  lsusb
  uname -a
  python3 -m koalabyte.main --self-test

Enable Jetson interfaces through NVIDIA Jetson-IO / device-tree configuration for your carrier board.
MSG
