# StaffWorkstation4Linux
This is a minimal implementation of the "3M Staff Workstation" software for Linux, which controls the 3M Bookcheck Unit Model 940 Series (especially tested with Model 942) via USB and the related barcode scanner (a [Microscan MS-820](https://files.microscan.com/downloadcenter/ms820manual.pdf)) via serial RS232.

You can adapt this script to automatically switch operating modes of the device based on your needs and workflows.

## Hardware Setup
Allow non-root users communication with the USB device. Replace the vendor/device id for your device model.

```
#/etc/udev/rules.d/99-bookcheck.rules:
ATTR{idVendor}=="0d2c", ATTR{idProduct}=="03ae", MODE="0666"
```

Disable serial-getty for exclusive serial port access and add your user to the dialout group for non-root access.
```
sudo systemctl mask serial-getty@ttyAMA0.service
sudo systemctl mask serial-getty@serial0.service
usermod -aG dialout <linuxuser>
reboot
```

## Software Setup
Install the necessary python packages (requirements.txt).
```
apt install wmctrl python3-usb python3-serial python3-tk python3-dev python3-pip
sudo pip3 install pyautogui
```

## Configuration
On startup, both scripts will try to read the config file `~/.config/staffworkstation4linux.ini`, which can contain the following settings. If it does not exist, the following defaults will be used.
```
[bookcheck]
idvendor = 0d2c
idproduct = 03ae
keywordcheckout = Ausleihe
keywordcheckin = Rückgabe

[scanner]
port = /dev/ttyS0
rate = 9600
init = <Kr1,0,0,8,10><Kg1><H><A>
sleep = 1.5
```

The caracters given in `init` will be sent over the serial port to the scanner in order to initialize it with your desired settings. Please have a look at the scanner manual (linked above) for all command codes. In this example:
- `<Kr1,0,0,8,10>` enables barcode type "Interleaved 2 of 5"
- `<Kg1>` sets read mode "Continuous Read 1 Output"
- `<H>` ensures that the laser is on
- `<A>` applies the settings

`sleep` is the delay the scanner gets deactivated after a successful read.

## Usage
```
### Bookcheck: read device status ###
./bookchecker.py
status 1: 01010000 (check-in, normal-mode, verifier-off, auto)
status 2: 00000001010001ee00 (sensor-not-triggered, left, verifier-off)

### Bookcheck: set device mode manually ###
# i = check-in (incoming), o = check-out (outgoing)
# x = normal processing mode, y = magnetic media mode
# a = automatic mode, m = manual mode
# l = verifier light on, k = verifier light off
./bookchecker.py o y
status 1: 01010000 (check-in, normal-mode, verifier-off, auto)
status 2: 00000001010001ee00 (sensor-not-triggered, left, verifier-off)
set resp: 00000000 (check-out, magnetic-media-mode, verifier-off, auto)

### Bookcheck: set device mode automatically based on titles of open windows ###
./bookchecker.py background
status 1: 00000000 (check-out, magnetic-media-mode, verifier-off, auto)
status 2: 00000000000001de00 (sensor-not-triggered, left, verifier-off)
Found window title Rückgabe, switch to check-in
set resp: 01000000 (check-in, magnetic-media-mode, verifier-off, auto)

### Scanner: start listening for scanned barcodes ###
./bookscanner.py
```

## BTW
In a [flyer](https://multimedia.3m.com/mws/media/602271O/940-series-bookcheck.pdf) of this device, the serial barcode scanner is called "a state-of-the-art barcode scanner", hehe.
