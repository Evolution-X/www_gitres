## THESE INSTRUCTIONS ASSUME YOUR DEVICE'S BOOTLOADER IS ALREADY UNLOCKED

1. Download recovery, rom for beryllium from [here](https://sourceforge.net/projects/evolution-x/files/beryllium/15/).
2. Reboot to bootloader.
3.
```fastboot flash recovery recovery.img```

4. Reboot to recovery.
5. While in recovery, navigate to **Factory Reset** → **Format Data/Factory Reset** and confirm to format the device.
6. When done formatting, go back to the main menu and then navigate to **Apply Update** → **Apply from ADB**.
7. `adb sideload rom.zip` (replace "rom.zip" with the actual build filename).
8. (Optional) Reboot to recovery (fully) to sideload any add-ons.
9. Reboot to system and **#KeepEvolving**.
