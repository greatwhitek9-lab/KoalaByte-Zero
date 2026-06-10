#!/bin/bash
# Enable wireless monitor mode
sudo modprobe -r brcmfmac
sudo modprobe brcmfmac

# Enable SPI for display (Jetson/Ubuntu-based boards may use different config locations)
if [ -f /boot/firmware/config.txt ]; then
  echo "dtparam=spi=on" | sudo tee -a /boot/firmware/config.txt
  echo "Appended dtparam=spi=on to /boot/firmware/config.txt"
else
  echo "Warning: /boot/firmware/config.txt not found; please enable SPI in your board's configuration manually."
fi
