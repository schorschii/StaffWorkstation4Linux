# StaffWorkstation4Linux
This is a minimal implementation of the "3M Staff Workstation" software for Linux, which controls the 3M Bookcheck Unit Model 940 Series (especially tested with Model 942) via USB and the related barcode scanner (a [Microscan MS-820](https://files.microscan.com/downloadcenter/ms820manual.pdf)) via serial RS232.

You can adapt this script to automatically switch operating modes of the device based on your needs and workflows.

## Hardware Setup
Allow non-root users communication with the USB device. Replace the vendor/device id for your device model.

```
#/etc/udev/rules.d/50-bookcheck.rules:
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
requiredgoodreads = 3
init = <Kr1,0,0,8,10><A>
```

The caracters given in `init` will be sent over the serial port to the scanner in order to initialize it with your desired settings. In this example, it enables barcode type "Interleaved 2 of 5". Please have a look at the scanner manual (linked above) for all command codes.

## Usage
```
### Bookcheck: read device status ###
./bookchecker.py
status 1: 00010001 (check-out, normal-mode)
status 2: 0d000000010001fe00

### Bookcheck: set device mode manually ###
# i = check-in (incoming), o = check-out (outgoing)
# x = normal processing mode, y = magnetic media mode
./bookchecker.py i y
status 1: 00010001 (check-out, normal-mode)
status 2: 0d000000010001fe00
set resp: 01000001 (check-in, magnetic-media-mode)

### Bookcheck: set device mode automatically based on open windows ###
./bookchecker.py a
status 1: 01010001 (check-in, normal-mode)
status 2: 0d000001010001ee00
Found window title Ausleihe, switch to check-out
set resp: 00010001 (check-out, normal-mode)

### Scanner: start listening for scanned barcodes ###
./bookscanner.py
```

## BTW
In a [flyer](https://multimedia.3m.com/mws/media/602271O/940-series-bookcheck.pdf) of this device, the serial barcode scanner is called "a state-of-the-art barcode scanner", hehe.
