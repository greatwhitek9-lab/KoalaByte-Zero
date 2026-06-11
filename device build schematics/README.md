# Device Build Schematics — Koalabyte Zero Rev0.5 Version B

This folder contains the normalized Koalabyte Zero Rev0.5 Version B prototype production starter package.

Applied mismatch fixes and voice hardware updates:

1. Display normalized to **DS1 3.5 inch HDMI touchscreen, 800x480, 5V**.
2. Camera normalized to **CAM1 IMX708 CSI camera module** centered just above the eyes and below the enlarged ears.
3. Power upgraded to **REG1 5V 12A** main rail with 10A-class protection.
4. `SW_PWR` normalized as a valid rear/back-mounted power switch, not a malformed BOM/PnP row.
5. `HUB1` retained as the powered internal USB 3.0 hub for SDR, Wi-Fi, debug, and USB touch.
6. `SPK1` retained as the speaker/buzzer UI alert and optional AI pet voice-response output component.
7. **MIC1 added as the right-ear I2S MEMS microphone** for KoalaByte AI pet speech input, `KillerKoala` wake word detection, and voice-to-AI-pet interaction.
8. `J12` / `J_MIC` added as the right-ear microphone harness carrying `3V3`, `GND`, `I2S_BCLK`, `I2S_LRCLK`, `I2S_DIN`, and `SHIELD/NC`.
9. Connector/control mapping aligned with repo config: EYE1 dual LCD board, J10/SW1-SW8 controls, rear SW_PWR, top IR RX/TX, default 3 external antennas, optional LTE fourth antenna only.

Expected package contents:

```text
MANIFEST.txt
Assembly/ASSEMBLY_README.md
Assembly/KoalaByte_Rev0_5_VersionB_PickAndPlace.csv
BOM/KoalaByte_Rev0_5_VersionB_BOM.csv
Docs/KoalaByte_Rev0_5_VersionB_Net_Summary.txt
Docs/Koalabyte_Zero_Rev0_5_Placement_Update.md
Drill/KoalaByte_Rev0_5_VersionB.drl
Gerber/KoalaByte_Rev0_5_VersionB-Edge_Cuts.gm1
Gerber/KoalaByte_Rev0_5_VersionB-F_Cu.gtl
Gerber/KoalaByte_Rev0_5_VersionB-F_Mask.gts
Gerber/KoalaByte_Rev0_5_VersionB-F_SilkS.gto
KiCad/KoalaByte_Rev0_5_VersionB.kicad_pcb
KiCad/KoalaByte_Rev0_5_VersionB.kicad_pro
KiCad/KoalaByte_Rev0_5_VersionB.kicad_sch
Mechanical/MECHANICAL_STARTER_NOTES.md
```

Important: these are prototype interface-shield/harness-board starter files, not manufacturer-verified production files. Run ERC/DRC, footprint verification, connector pin validation, power integrity review, thermal testing, enclosure-fit checks, audio capture testing, acoustic-port validation, and at least one physical test spin before ordering production boards.
