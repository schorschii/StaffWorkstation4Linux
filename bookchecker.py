#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from threading import Timer
import configparser
import usb.core
import usb.util
import serial
import time
import sys
import os


# retrieve status
def getStatusText1(status1):
    return (
        ('check-in' if status1[0] else 'check-out') +', '+
        ('normal-mode' if status1[1] else 'magnetic-media-mode') +', '+
        ('verifier-on' if status1[2] else 'verifier-off') +', '+
        ('manual' if status1[3] else 'auto')
    )
def getStatusText2(status2):
    verifierIndicator = status2[7] & 0b00001000
    return (
        ('sensor-triggered' if status2[2] else 'sensor-not-triggered') +', '+
        ('left' if status2[6]==1 else 'right' if status2[6]==2 else 'unknown-direction') +', '+
        ('verifier-off' if verifierIndicator else 'verifier-on')
    )
def getStatus(dev, verbose=True):
    status1 = dev.ctrl_transfer(0xC0, 0xbd, 0xffff, 0xffff, 9)
    bInOut         = status1[0]
    bMediaMode     = status1[1]
    bVerifierLight = status1[2]
    bAutoMode      = status1[3]
    if verbose: print('status 1:', bytes(status1).hex(), '('+getStatusText1(status1)+')')

    status2 = dev.ctrl_transfer(0xC0, 0xb7, 0x0000, 0x0000, 9)
    if verbose: print('status 2:', bytes(status2).hex(), '('+getStatusText2(status2)+')')

    return bInOut, bMediaMode, bAutoMode, bVerifierLight

# set status
def sendStatusUpdate(dev, bInOut, bMediaMode, bAutoMode=0xff, bVerifierLight=0xff):
    # 0xff = no change
    # 0x01 = enable feature
    # 0x00 = disable feature
    status1 = (bMediaMode << 8) | bInOut
    status2 = (bAutoMode << 8) | bVerifierLight
    statusResponse = dev.ctrl_transfer(0xC0, 0xbd, status1, status2, 9)
    print('set resp:', bytes(statusResponse).hex(), '('+getStatusText1(statusResponse)+')')

# connected mode
def scannerWakeup(dev, ser, sensorTriggeredCmd, sensorUntriggeredCmd):
    lastSensorState = True
    while True:
        status2 = dev.ctrl_transfer(0xC0, 0xb7, 0x0000, 0x0000, 9)
        if status2[2] and not lastSensorState:
            lastSensorState = True
            ser.write(sensorTriggeredCmd.encode('ascii'))
        elif not status2[2] and lastSensorState:
            lastSensorState = False
            ser.write(sensorUntriggeredCmd.encode('ascii'))
        time.sleep(0.05)

# auto mode
def autoModeChanger(dev, keywordCheckout, keywordCheckin):
    while True:
        bInOut, bMediaMode, bAutoMode, bVerifierLight = getStatus(dev, verbose=False)
        for line in os.popen('wmctrl -l').read().splitlines():
            if keywordCheckout.upper() in line.upper():
                if bInOut == 0x00: break
                print(f'--> found window title {keywordCheckout}, switch to check-out')
                sendStatusUpdate(dev, 0x00, bMediaMode)
            elif keywordCheckin.upper() in line.upper():
                if bInOut == 0x01: break
                print(f'--> found window title {keywordCheckin}, switch to check-in')
                sendStatusUpdate(dev, 0x01, bMediaMode)
        time.sleep(1)

def main():
    # read config
    config = {}
    configFile = str(Path.home())+'/.config/staffworkstation4linux.ini'
    configParser = configparser.ConfigParser()
    configParser.read(configFile)
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

    bInOut, bMediaMode, bAutoMode, bVerifierLight = getStatus(dev)

    changed = False
    auto    = False
    for arg in sys.argv:
        if arg == sys.argv[0]: continue

        if arg == 'background':
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

        if arg == 'a':
            bAutoMode = 0x00
            changed = True
        if arg == 'm':
            bAutoMode = 0x01
            changed = True

        if arg == 'l':
            bVerifierLight = 0x01
            changed = True
        if arg == 'k':
            bVerifierLight = 0x00
            changed = True

    # set mode as given by command line parameter
    if changed:
        sendStatusUpdate(dev, bInOut, bMediaMode, bAutoMode, bVerifierLight)

    if auto:
        # setup connected scanner mode (activate scanner when bookcheck sensor triggered)
        sensorTriggeredCmd = config.get('sensortriggeredcmd', None)
        sensorUntriggeredCmd = config.get('sensoruntriggeredcmd', None)
        if sensorTriggeredCmd or sensorUntriggeredCmd:
            scannerConfig = {}
            scannerConfigParser = configparser.ConfigParser()
            scannerConfigParser.read(configFile)
            if(scannerConfigParser.has_section('scanner')):
                scannerConfig = dict(scannerConfigParser.items('scanner'))
            ser = serial.Serial(
                scannerConfig.get('port', '/dev/ttyS0'),
                int(scannerConfig.get('rate', 9600)),
            )
            print('Connected to scanner:', ser.name)
            t = Timer(1, scannerWakeup, [dev, ser, sensorTriggeredCmd, sensorUntriggeredCmd])
            t.daemon = True
            t.start()

        # setup window title listener for automatic mode change based on open windows
        keywordCheckout = config.get('keywordcheckout', 'Ausleihe')
        keywordCheckin  = config.get('keywordcheckin', 'Rückgabe')
        t2 = Timer(1, autoModeChanger, [dev, keywordCheckout, keywordCheckin])
        t2.daemon = True
        t2.start()

        while True:
            time.sleep(1)

if(__name__ == '__main__'):
    main()
