#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import usb.core
import usb.util
import sys

# find device and init connection
dev = usb.core.find(idVendor=0x0d2c, idProduct=0x03ae)
if dev is None:
    raise ValueError('3M Bookcheck USB device not found')
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
for arg in sys.argv:
    if arg == sys.argv[0]: continue

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

if changed:
    sendStatusUpdate(bInOut, bMediaMode)
