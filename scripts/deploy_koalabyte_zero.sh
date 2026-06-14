#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-$HOME/koalabyte-zero-runtime}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-dir)
      INSTALL_DIR="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: scripts/deploy_koalabyte_zero.sh [--install-dir PATH]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 2
      ;;
  esac
done

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Missing required command: $PYTHON_BIN" >&2
  exit 1
fi

if [[ ! -f "$REPO_DIR/requirements.txt" ]]; then
  echo "Run this script from a complete KoalaByte Zero checkout." >&2
  exit 1
fi

mkdir -p "$INSTALL_DIR"
if command -v rsync >/dev/null 2>&1; then
  rsync -a --exclude .git --exclude .venv --exclude __pycache__ --exclude '*.pyc' "$REPO_DIR/" "$INSTALL_DIR/"
else
  cp -R "$REPO_DIR/." "$INSTALL_DIR/"
fi

cd "$INSTALL_DIR"
"$PYTHON_BIN" -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if [[ -f pyproject.toml ]]; then
  python -m pip install -e . || true
fi

python -m koalabyte.main --print-config >/tmp/koalabyte_zero_config.json
python -m koalabyte.main --self-test
if [[ -d tests ]]; then
  python -m pytest -q
fi

echo "KoalaByte Zero deploy verification completed. Runtime folder: $INSTALL_DIR"
echo "Config snapshot: /tmp/koalabyte_zero_config.json"
