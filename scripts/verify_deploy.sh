#!/usr/bin/env bash
set -euo pipefail

python3 -m koalabyte.main --print-config >/tmp/koalabyte_config.json
python3 -m koalabyte.main --self-test
python3 -m pytest -q

echo "KoalaByte deploy verification passed."
