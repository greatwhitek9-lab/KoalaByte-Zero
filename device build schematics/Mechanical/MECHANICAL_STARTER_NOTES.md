# KoalaByte Rev0.5 Version B Mechanical Starter Dimensions

Concept envelope target:

- Overall handheld front: approx. 155 mm W x 115 mm H x 35-55 mm D depending on Jetson heatsink, battery, and antenna routing.
- Interface shield PCB in this package: 120 mm W x 85 mm H.
- Mounting holes: M3 at 5,5 / 115,5 / 115,80 / 5,80 mm.

Use this only as a layout starter. Final enclosure CAD must be derived from the exact display, Jetson dev kit, battery, internal USB hub, ESP32-S3 dual-eye LCD board, and antenna hardware models.

## Rev0.5 eye/display module update

- Reserve a front-face mount above the 3.5 inch 800x480 touchscreen for **EYE1: ESP32-S3 1.28inch Double Eye Round LCD AIoT Development Board, Onboard Dual 1.28inch IPS Displays**.
- Validate exact board width, height, USB/header access, heat clearance, and cable strain relief before production enclosure release.
- Legacy LED-ring-only eye mounts are not the current Rev0.5 eye baseline.

## Rev0.5 camera placement

- CAM1 is normalized to **IMX708 CSI**.
- Place CAM1 in the **nose pod / central front nose assembly between the two EYE1 round LCD displays**.
- Reserve lens opening, FFC bend radius, and strain relief.

## Rev0.5 rear power switch

- Remove the front/nose power switch concept from the enclosure design.
- Add a rear/back-mounted SW_PWR on/off switch with finger clearance and strain relief for its harness.
- SW_PWR may be a true high-current disconnect or a logic/regulator-enable switch depending on the final power architecture.

## Power and thermal notes

- REG1 is now a 5V 10-12A path. Provide airflow and thermal clearance.
- F1 is now 10A-class input protection. Validate fuse/current behavior under full Jetson + display + USB + radio load.
- Keep battery/BMS and high-current wiring away from GPS patch antenna, SDR coax, and NFC coil.
- Use keyed/locking connectors where possible.

## Antenna notes

Default build has 3 external antennas only:

1. Wi-Fi/Bluetooth whip antenna.
2. LoRa/Sub-GHz whip antenna.
3. SDR antenna.

Optional LTE fourth antenna is DNP unless an LTE variant is built. GPS uses a top/rear active patch antenna. NFC uses an internal left-ear coil.
