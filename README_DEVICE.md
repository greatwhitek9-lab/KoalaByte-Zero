# Koalabyte Firmware — Device Installation & Run Guide

WARNING & SAFETY
- Work only on devices you own or are authorized to test.
- Battery systems can be dangerous. Verify BMS, fuses, and wiring before powering the system.
- Follow local regulations when using RF devices (sub-GHz, SDR).

Hardware prerequisites
- Jetson Orin Nano (or equivalent carrier) with a supported Linux image.
- DS1: 3.5" HDMI LCD connected to HDMI port.
- CAM1: IMX708 CSI camera connected to the CSI port and secured.
- BAT1 / BMS1: Installed battery pack and BMS, fuse F1 and regulator REG1 in place.
- Optional peripherals: ESP32-S3 (U2), NFC (U_RF2), BLE (U_RF3), WiFi/BT (U_RF1), GPS1, SDR1, etc.

Software prerequisites (on-device)
- Debian/Ubuntu-based Jetson OS recommended (matching GPU/libcamera support).
- Python 3.10+ (3.11 recommended).
- System packages: git, python3-venv, build-essential, python3-dev.
- Optional: libcamera, v4l2-utils for camera support; drivers for SDR/GPS/peripherals as needed.
- Install Python runtime dependencies (requirements.txt — create if you maintain runtime deps).

Install steps
1. Clone repo and enter it:
   git clone https://github.com/greatwhitek9-lab/koalabyte-firmware.git
   cd koalabyte-firmware

2. Create and activate a venv:
   python3 -m venv venv
   source venv/bin/activate

3. Install runtime dependencies:
   pip install --upgrade pip
   pip install -r requirements.txt
   # If you don't have a requirements.txt, at minimum install:
   pip install pyyaml
   # Install cyberpet_ai or provide a local stub config if not available

Configuration
- Provide the config module expected by the firmware:
  - The code expects functions: get_hardware_config(), get_cyberpet_config(), get_security_config(), get_ui_config().
  - Create config/config.py or a module on PYTHONPATH. A simple pattern:
    - cp config/examples/config_template.py -> config/config.py
    - Edit values (voltage_reader/temp_reader can be set to callables)
- docs/bom.yaml is present and used by the loader; update it if hardware changes.
- Environment variables for simulation/testing:
  - KOALA_BATT_V — simulate battery voltage (e.g., 7.95)
  - KOALA_BATT_C — simulate battery temperature (e.g., 29.6)

Run the firmware (manual)
1. Activate venv:
   source venv/bin/activate
2. Run:
   python3 "Koalabyte New Main Code.py"
3. Check runtime logs:
   - stdout shows startup messages
   - /var/log/koalabyte/koalabyte_combined.log contains structured logs

Run the firmware as a systemd service (example)
1. Create a unit file /etc/systemd/system/koalabyte.service:
   [Unit]
   Description=Koalabyte Firmware
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/path/to/koalabyte-firmware
   ExecStart=/path/to/koalabyte-firmware/venv/bin/python3 "/path/to/koalabyte-firmware/Koalabyte New Main Code.py"
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=multi-user.target

2. Enable and start:
   sudo systemctl daemon-reload
   sudo systemctl enable --now koalabyte
3. Monitor:
   sudo journalctl -u koalabyte -f
   or check /var/log/koalabyte/koalabyte_combined.log

Verify KillerKoala and SafetyInterlock
- Logs: look for “KillerKoala awakening...” and its greeting if cyberpet_ai and config are present.
- If cyberpet_ai or the config module is missing, the system logs warnings and continues in a degraded mode.
- To enable lab-only functions: call device.safety.acknowledge_lab_mode() in an interactive session or implement a safe path in config to set lab mode.

Battery & hardware checks (recommended)
- With the battery disconnected, verify regulator and BMS wiring visually.
- Apply power and measure TP_BAT pads with a multimeter before connecting sensitive peripherals.
- Confirm fuse F1 value is correct (10A resettable recommended) and regulator thermals are acceptable under load.

Troubleshooting
- Missing module errors: ensure config and cyberpet_ai are installed and PYTHONPATH includes repo/config if used.
- Camera/display issues: verify libcamera, HDMI cable orientation, and that display drivers are functional.
- RF/peripheral issues: ensure kernel drivers and firmware are installed for GPS/SDR modules.

Maintenance & updating
- Pull updates via git and restart the service.
- Recommended workflow: feature branch -> PR -> CI -> merge to main.
- Regenerate docs/bom.yaml from legacy docs/BOM with:
  python3 scripts/convert_bom_to_yaml.py

Contact & notes
- Open issues in the repository for bugs and feature requests.
- Ensure all RF usage complies with local regulations.
