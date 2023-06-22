# StaffWorkstation4Linux
This is a minimal implementation of the "3M Staff Workstation" software for Linux, which controls the 3M Bookcheck Unit Model 940 Series (especially tested with Model 942) via USB.

You can adapt this script to automatically switch operating modes of the device based on your needs and workflows.

## Usage
```
### read device status ###
./bookchecker.py
status 1: 00010001 (check-out, normal-mode)
status 2: 0d000000010001fe00

### set device mode ###
# i = check-in (incoming), o = check-out (outgoing)
# x = normal processing mode, y = magnetic media mode
./bookchecker.py i y
status 1: 00010001 (check-out, normal-mode)
status 2: 0d000000010001fe00
set resp: 01000001 (check-in, magnetic-media-mode)
```
