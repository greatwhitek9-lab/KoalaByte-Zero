# KoalaByte Firmware Installation Guide

### Prerequisites
Ensure you have the following ready:
- **Hardware:**
  - NVIDIA Jetson Orin Nano Super with 8GB RAM
  - ESP32-S3-WROOM MCU module
  - USB-C cable for development
- **Software:**
  - JetPack 5.1+ OS image
  - Python 3.11 or higher
  - `sdkmanager` (installed for the JetPack setup)
  - **ESP toolchain**:
    - Install the ESP-IDF (Espressif IoT Development Framework)
    - Required Python development libraries: `pyserial`, `esptool`, etc.
- **Additional Requirements:**
  - Linux development machine for cross-compilation
  - Reliable internet connection for downloading tools and firmware dependencies

---

### Step 1: Set Up Jetson Orin Nano Super

#### Install JetPack 5.1+
1. Open a terminal on your Linux development machine.
2. Download and install JetPack on the Jetson device using the following command:
   ```bash
   sdkmanager --cli install --logintype devzone --product Jetson \
     --version 5.1.2 --target Jetson_Orin_Nano_Super
   ```
3. Follow the on-screen instructions to configure and verify the Jetson setup.

---

### Step 2: Set Up ESP32-S3-WROOM

#### Install ESP-IDF (IoT Development Framework for ESP32)
1. Clone the ESP-IDF repository:
   ```bash
   git clone --recursive https://github.com/espressif/esp-idf.git
   cd esp-idf
   ./install.sh
   export PATH="$HOME/esp/esp-idf/export:$PATH"
   ```
2. Verify installation:
   ```bash
   idf.py --version
   ```

#### Flash Firmware to ESP32-S3
1. Connect the ESP32 device to the development machine via a USB-C cable.
2. Put the ESP32 in boot mode:
   - Hold the "BOOT" button while pressing and releasing the "EN (Reset)" button.
3. Use `esptool.py` to flash the firmware:
   ```bash
   esptool.py --chip esp32s3 erase_flash
   esptool.py --chip esp32s3 write_flash -z 0x1000 firmware.bin
   ```
4. Reboot the device after flashing.

#### Install Dependencies for ESP32
Ensure the following Python libraries are installed:
```bash
pip install pyserial esptool
```

---

### Additional Enhancements

1. **Automatic Scripts:**
   - Scripts need to be developed to automate repetitive tasks such as:
     - Firmware flashing (`esptool.py` commands)
     - Installation of development dependencies.
   - Example:
     ```bash
     #!/bin/bash
     # This bash script automates flashing and dependency setup
     pip install --user pyserial esptool
     esptool.py --chip esp32s3 erase_flash
     esptool.py --chip esp32s3 write_flash -z 0x1000 firmware.bin
     ```

2. **Docker Support:**
   - Create Dockerfiles to ensure consistency in development environments:
     - Base image can contain all the necessary dependencies for:
       - Cross-compiling for Jetson / ESP32.
       - Pre-installed tools like `sdkmanager` and `IDF`.
     - Example `Dockerfile` for ESP32 cross development:
       ```Dockerfile
       FROM ubuntu:20.04
       RUN apt-get update && apt-get install -y python3 python3-pip git \
           && pip3 install pyserial esptool
       ```

3. **Hardware Connections:**
   - The ESP32-S3 communicates with the Jetson Orin Nano Super primarily through:
     - **UART**: Ensure baud rates and serial connections are correctly configured.
     - **GPIO**: Pin mappings in the firmware must match hardware specs.
     - **SPI**: Optional for high-speed communication but requires clock sync.

4. **Testing Firmware:**
   - After flashing the firmware on the ESP32:
     - Use `miniterm.py` (from `pyserial`) to monitor the boot logs:
       ```bash
       miniterm.py /dev/ttyUSB0 115200
       ```
     - Verify connectivity between Jetson and ESP32 by running a handshake script.

5. **Error Handling:**
   - Common issues and resolutions include:
     - **Jetson Setup Issues:**
       - *Error:* `sdkmanager` fails midway.
       - *Solution:* Retry with the `--clean` option or check log paths like `/var/log/sdkmanager.log`.
     - **ESP32 Boot Failure:**
       - *Error:* No boot logs seen on `miniterm.py`.
       - *Solution:* Double-check boot-mode; ensure USB cable is connected to power and data-supported port.
     - **General Problems:**
       - Google ESP32-S3 and NVIDIA forums.