## THESE INSTRUCTIONS ASSUME YOUR DEVICE'S BOOTLOADER IS ALREADY UNLOCKED


1. Download recovery, rom for sapphire from [https://sourceforge.net/projects/evolution-x/files/sapphire/14/](https://sourceforge.net/projects/evolution-x/files/sapphire/14/)
2. Reboot to bootloader
3.
```fastboot flash recovery recovery.img```

```fastboot reboot recovery```


4. While in recovery, navigate to Factory reset -> Format data/factory reset and confirm to format the device.
5. When done formatting, go back to the main menu and then navigate to Apply update -> Apply from ADB
6. adb sideload rom.zip (replace "rom" with actual filename)
7. (optional) Reboot to recovery (fully) to sideload any add-ons
8. Reboot to system & #KeepEvolving
