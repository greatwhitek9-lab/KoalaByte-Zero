#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "KoalaByte Jetson setup complete. Run: python3 -m koalabyte.main --self-test"
