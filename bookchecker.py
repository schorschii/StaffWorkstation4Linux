#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import configparser
import usb.core
import usb.util
import time
import sys
import os


# read config
config = {}
configParser = configparser.ConfigParser()
configParser.read(str(Path.home())+'/.config/staffworkstation4linux.ini')
if(configParser.has_section('bookcheck')): config = dict(configParser.items('bookcheck'))

# find device and init connection
idVendor = int.from_bytes(bytes.fromhex(config.get('idvendor', '0d2c')), byteorder='big')
idProduct = int.from_bytes(bytes.fromhex(config.get('idproduct', '03ae')), byteorder='big')
dev = usb.core.find(
    idVendor = idVendor,
    idProduct = idProduct
)
if dev is None:
    raise ValueError(f'3M Bookcheck USB device (ven={hex(idVendor)}, dev={hex(idProduct)}) not found')
dev.set_configuration()
#print(dev.get_active_configuration())

# retrieve status
def getStatusText(bInOut, bMediaMode):
    return ('check-in' if bInOut else 'check-out') +', '+ ('normal-mode' if bMediaMode else 'magnetic-media-mode')

status1    = dev.ctrl_transfer(0xC0, 0xbd, 0xffff, 0xffff, 9)
bInOut     = status1[0]
bMediaMode = status1[1]
print('status 1:', bytes(status1).hex(), '('+getStatusText(bInOut, bMediaMode)+')')

status2 = dev.ctrl_transfer(0xC0, 0xb7, 0x0000, 0x0000, 9)
print('status 2:', bytes(status2).hex())

# set status
def sendStatusUpdate(bInOut, bMediaMode):
    status = (bMediaMode << 8) | bInOut
    ret = dev.ctrl_transfer(0xC0, 0xbd, status, 0x01ff, 9)
    print('set resp:', bytes(ret).hex(), '('+getStatusText(bInOut, bMediaMode)+')')

changed = False
auto    = False
for arg in sys.argv:
    if arg == sys.argv[0]: continue

    if arg == 'a':
        auto = True

    if arg == 'i':
        bInOut = 0x01
        changed = True
    if arg == 'o':
        bInOut = 0x00
        changed = True

    if arg == 'x':
        bMediaMode = 0x01
        changed = True
    if arg == 'y':
        bMediaMode = 0x00
        changed = True

# set mode as given by command line parameter
if changed:
    sendStatusUpdate(bInOut, bMediaMode)

# setup window title listener for automatic mode change based on open windows
if auto:
    keywordCheckout = config.get('keywordcheckout', 'Ausleihe')
    keywordCheckin  = config.get('keywordcheckin', 'Rückgabe')
    while True:
        for line in os.popen('wmctrl -l').read().splitlines():
            if keywordCheckout.upper() in line.upper():
                if bInOut == 0x00: break
                print(f'Found window title {keywordCheckout}, switch to check-out')
                bInOut = 0x00
                sendStatusUpdate(bInOut, bMediaMode)
            elif keywordCheckin.upper() in line.upper():
                if bInOut == 0x01: break
                print(f'Found window title {keywordCheckin}, switch to check-in')
                bInOut = 0x01
                sendStatusUpdate(bInOut, bMediaMode)
        time.sleep(1)
