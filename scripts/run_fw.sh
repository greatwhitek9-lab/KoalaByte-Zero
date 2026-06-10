#!/bin/bash
# Run the firmware script for KoalaByte (normalized path)
# Ensure you are in the project root directory
cd "$(dirname "$0")/.." || exit 1

# Run the canonical firmware entrypoint
python3 "Koalabyte New Main Code.py"
