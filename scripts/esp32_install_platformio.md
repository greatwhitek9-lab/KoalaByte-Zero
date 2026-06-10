# ESP32 PlatformIO Installation Guide

### Prerequisites
To follow this guide, ensure you have:
- Python 3.7 or higher installed [Download Python](https://www.python.org/downloads/)
- A stable internet connection to download the PlatformIO package.

---

### Step 1: Install PlatformIO
1. **Install Python Dependencies (Optional):**
   It's recommended to use a virtual environment for isolated development:
   ```bash
   python -m venv pio-env
   source pio-env/bin/activate
   ```

2. **Install PlatformIO:**
   Install PlatformIO globally (system-wide) using pip:
   ```bash
   pip install platformio
   ```

   Alternatively, in a virtual environment:
   ```bash
   pip install platformio
   ```

---

### Step 2: Initialize PlatformIO for ESP32
1. Check if PlatformIO is installed correctly:
   ```bash
   platformio --version
   ```
2. Start a new ESP32 project:
   ```bash
   platformio project init --board esp32dev
   ```

3. Open the generated `platformio.ini` file to configure your project settings.

---

### Step 3: Additional Tips
- **Documentation:** Refer to the [PlatformIO Documentation](https://docs.platformio.org/) for detailed usage.
- **Troubleshooting:** If the `platformio` command is not found, ensure Python and pip are added to your system's PATH.
