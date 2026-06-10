# Koalabyte Firmware — Tests README

This document explains how to run the unit tests and smoke tests for the Koalabyte firmware repository.

Prerequisites
- Linux or macOS workstation (Ubuntu 20.04/22.04 recommended for parity with CI)
- Python 3.10+ (3.11 recommended)
- git
- (Optional) Docker if you prefer to run tests inside a container

Setup (local)
1. Clone the repository:
   git clone https://github.com/greatwhitek9-lab/koalabyte-firmware.git
   cd koalabyte-firmware

2. Create and activate a virtual environment:
   python3 -m venv venv
   source venv/bin/activate

3. Install development dependencies (used by CI and local tests):
   pip install --upgrade pip
   pip install -r requirements-dev.txt

Running the test suite
- Run the full pytest suite:
  pytest -q

- Run a single test file (example):
  pytest -q tests/test_bom_loader.py

- Run a single test function:
  pytest -q tests/test_battery.py::test_battery_readers

Environment variables used by tests / simulation
- KOALA_BATT_V — optional float string to override the default simulated battery voltage reader (example: 7.95)
- KOALA_BATT_C — optional float string to override the default simulated battery temperature reader (example: 29.6)

Example:
  export KOALA_BATT_V=7.95
  export KOALA_BATT_C=29.6
  pytest -q tests/test_battery.py::test_battery_readers

Regenerating docs/bom.yaml
If you update or maintain the legacy docs/BOM TSV file and want a structured YAML copy, use the converter script:
  python3 scripts/convert_bom_to_yaml.py

CI (GitHub Actions)
- The repository contains .github/workflows/ci.yml which:
  - checks out the code
  - sets up Python
  - installs dev dependencies from requirements-dev.txt
  - runs pytest
- CI runs on push and pull requests targeting main.

Interpreting failures
- Missing YAML/pyyaml errors: install PyYAML (pip install pyyaml) or ensure requirements-dev.txt is installed
- Import errors for runtime modules (config, cyberpet_ai): tests use defensive imports. Provide a minimal config module in PYTHONPATH when required.
- If tests fail due to BOM parsing issues, inspect docs/bom.yaml and the legacy docs/BOM file for formatting problems.

Notes
- Tests are minimal smoke tests intended to provide quick feedback and guardrails. Expand tests to increase coverage for edge cases and hardware-in-the-loop behaviors.
