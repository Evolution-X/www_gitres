## THESE INSTRUCTIONS ASSUME YOUR DEVICE'S BOOTLOADER IS ALREADY UNLOCKED


1. Download recovery, rom for beyond1lte from [here](https://sourceforge.net/projects/evolution-x/files/beyond1lte/15/)
2. Reboot to bootloader
3.
```heimdall flash --RECOVERY recovery.img```

4. Reboot to recovery
5. While in recovery, navigate to Factory reset -> Format data/factory reset and confirm to format the device.
6. When done formatting, go back to the main menu and then navigate to Apply update -> Apply from ADB
7. adb sideload rom.zip (replace "rom" with actual filename)
8. (optional) Reboot to recovery (fully) to sideload any add-ons
9. Reboot to system & #KeepEvolving
