#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtGui, QtCore

from pathlib import Path
from threading import Timer
import configparser
import usb.core
import usb.util
import serial
import time
import sys
import os


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    parentWidget  = None
    ICON_CHECKIN  = b'PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcKICAgaGVpZ2h0PSIyNHB4IgogICB2aWV3Qm94PSIwIC05NjAgOTYwIDk2MCIKICAgd2lkdGg9IjI0cHgiCiAgIHhtbG5zOmlua3NjYXBlPSJodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy9uYW1lc3BhY2VzL2lua3NjYXBlIgogICB4bWxuczpzb2RpcG9kaT0iaHR0cDovL3NvZGlwb2RpLnNvdXJjZWZvcmdlLm5ldC9EVEQvc29kaXBvZGktMC5kdGQiCiAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgPHBhdGgKICAgICBkPSJNIDY3OC45MzMzMywtOTYwIEggMjgxLjA2NjY3IEwgMCwtNjc4LjkzMzMzIHYgMzk3Ljg2NjY2IEwgMjgxLjA2NjY3LDAgSCA2NzguOTMzMzMgTCA5NjAsLTI4MS4wNjY2NyB2IC0zOTcuODY2NjYgeiIKICAgICBpZD0icGF0aDgyNyIKICAgICBzdHlsZT0iZmlsbDojYzgwMDAwO3N0cm9rZS13aWR0aDo1My4zMzMzIgogICAgIHNvZGlwb2RpOm5vZGV0eXBlcz0iY2NjY2NjY2NjIiAvPgogIDxwYXRoCiAgICAgZD0ibSAyNzQuMzQ3NjYsLTE4Ny4yODgxNCBjIC0yNi4yNDk5LDAgLTQ4LjQxMzgsLTkuMDM4OSAtNjYuNDkxNjQsLTI3LjExNjcgLTE4LjA3Nzc5LC0xOC4wNzc4MSAtMjcuMTE2NzEsLTQwLjI0MTY5IC0yNy4xMTY3MSwtNjYuNDkxNjYgdiAtMzk4LjIwNzAxIGMgMCwtMjYuMjQ5OTYgOS4wMzg5MSwtNDguNDEzODUgMjcuMTE2NzEsLTY2LjQ5MTY1IDE4LjA3Nzg0LC0xOC4wNzc4IDQwLjI0MTc0LC0yNy4xMTY3MSA2Ni40OTE2NCwtMjcuMTE2NzEgaCAyMDUuMDQ2OSB2IDkzLjYwODM2IGggLTIwNS4wNDY5IHYgMzk4LjIwNzAxIGggMjA1LjA0NjkgdiA5My42MDgzNyB6IgogICAgIGlkPSJwYXRoMiIKICAgICBzdHlsZT0iZmlsbDojZmZmZmZmO2ZpbGwtb3BhY2l0eToxO3N0cm9rZS13aWR0aDowLjc0MjkyMyIKICAgICBzb2RpcG9kaTpub2RldHlwZXM9InNzc3Nzc2NjY2NjY3MiIC8+CiAgPHBhdGgKICAgICBkPSJtIDYxMi4zNDIwNiwtNjY0LjI0NTAzIDY1LjM3NzIsNjYuMTIwMTggLTcxLjMyMDYsNzEuMzIwNjUgaCAyMTAuMjQ3NCB2IDkzLjYwODM3IGggLTIxMC4yNDc0IGwgNzEuMzIwNiw3MS4zMjA2NSAtNjUuMzc3Miw2Ni4xMjAyIC0xODMuNTAyLC0xODQuMjQ1MDMgeiIKICAgICBzdHlsZT0iZmlsbDojZmZmZmZmO2ZpbGwtb3BhY2l0eToxO3N0cm9rZS13aWR0aDoyOS43MTciCiAgICAgaWQ9InBhdGgxMjAxIiAvPgo8L3N2Zz4K'
    ICON_CHECKOUT = b'PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjxzdmcKICAgaGVpZ2h0PSIyNHB4IgogICB2aWV3Qm94PSIwIC05NjAgOTYwIDk2MCIKICAgd2lkdGg9IjI0cHgiCiAgIHhtbG5zOmlua3NjYXBlPSJodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy9uYW1lc3BhY2VzL2lua3NjYXBlIgogICB4bWxuczpzb2RpcG9kaT0iaHR0cDovL3NvZGlwb2RpLnNvdXJjZWZvcmdlLm5ldC9EVEQvc29kaXBvZGktMC5kdGQiCiAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiAgPGNpcmNsZQogICAgIHN0eWxlPSJvcGFjaXR5OjE7ZmlsbDojNGNhYjUzO2ZpbGwtb3BhY2l0eToxO3N0cm9rZS13aWR0aDowIgogICAgIGlkPSJwYXRoMTM0MSIKICAgICBjeD0iNDgwIgogICAgIGN5PSItNDgwLjAwMDAzIgogICAgIHI9IjQ4MCIgLz4KICA8cGF0aAogICAgIGQ9Im0gMjc0LjMzMDMyLC0xODcuMjgyMDEgYyAtMjYuMjUwNTEsMCAtNDguNDE0ODYsLTkuMDM5MSAtNjYuNDkzMDQsLTI3LjExNzI4IEMgMTg5Ljc1OTEsLTIzMi40Nzc0NyAxODAuNzIsLTI1NC42NDE4MiAxODAuNzIsLTI4MC44OTIzMyB2IC0zOTguMjE1MzQgYyAwLC0yNi4yNTA1MSA5LjAzOTEsLTQ4LjQxNDg2IDI3LjExNzI4LC02Ni40OTMwNCAxOC4wNzgxOCwtMTguMDc4MTggNDAuMjQyNTMsLTI3LjExNzI4IDY2LjQ5MzA0LC0yNy4xMTcyOCBoIDIwNS4wNTExOSB2IDkzLjYxMDMyIEggMjc0LjMzMDMyIHYgMzk4LjIxNTM1IGggMjA1LjA1MTE5IHYgOTMuNjEwMzIgeiIKICAgICBpZD0icGF0aDIiCiAgICAgc3R5bGU9ImZpbGw6I2ZmZmZmZjtmaWxsLW9wYWNpdHk6MTtzdHJva2Utd2lkdGg6MC43NDI5MzkiCiAgICAgc29kaXBvZGk6bm9kZXR5cGVzPSJzc3Nzc3NjY2NjY2NzIiAvPgogIDxwYXRoCiAgICAgZD0ibSA2MzMuMTM0MTIsLTI5NS43NTExMyAtNjUuMzc4NjIsLTY2LjEyMTU2IDcxLjMyMjE4LC03MS4zMjIxNCBoIC0yMTAuMjUxOCB2IC05My42MTAzMyBoIDIxMC4yNTE4IEwgNTY3Ljc1NTUsLTU5OC4xMjczIDYzMy4xMzQxMiwtNjY0LjI0ODg4IDgxNi42NCwtNDgwIFoiCiAgICAgc3R5bGU9ImZpbGw6I2ZmZmZmZjtmaWxsLW9wYWNpdHk6MTtzdHJva2Utd2lkdGg6MjkuNzE3NiIKICAgICBpZD0icGF0aDEyMDEiIC8+Cjwvc3ZnPgo='
    def __init__(self, icon, parent):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.parentWidget = parent
        menu = QtWidgets.QMenu(parent)
        exitAction = menu.addAction('Exit')
        exitAction.triggered.connect(self.exit)
        self.setContextMenu(menu)
        self.activated.connect(self.showMenuOnTrigger)
        self.setToolTip('3M Bookchecker')
    def showMenuOnTrigger(self, reason):
        if(reason == QtWidgets.QSystemTrayIcon.Trigger):
            self.contextMenu().popup(QtGui.QCursor.pos())
    def setSvgIcon(self, svg):
        ba = QtCore.QByteArray.fromBase64(svg)
        img = QtGui.QImage()
        img.loadFromData(ba, 'SVG')
        pm = QtGui.QPixmap(img)
        self.setIcon(QtGui.QIcon(pm))
    def exit(self):
        QtCore.QCoreApplication.exit()

# retrieve status
def getStatusText1(status1, trayIcon=None):
    if(trayIcon):
        if(status1[0]): trayIcon.setSvgIcon(SystemTrayIcon.ICON_CHECKIN)
        else: trayIcon.setSvgIcon(SystemTrayIcon.ICON_CHECKOUT)
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
def sendStatusUpdate(dev, bInOut, bMediaMode, bAutoMode=0xff, bVerifierLight=0xff, trayIcon=None):
    # 0xff = no change
    # 0x01 = enable feature
    # 0x00 = disable feature
    status1 = (bMediaMode << 8) | bInOut
    status2 = (bAutoMode << 8) | bVerifierLight
    statusResponse = dev.ctrl_transfer(0xC0, 0xbd, status1, status2, 9)
    print('set resp:', bytes(statusResponse).hex(), '('+getStatusText1(statusResponse, trayIcon)+')')

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
def autoModeChanger(dev, keywordCheckout, keywordCheckin, trayIcon=None):
    while True:
        bInOut, bMediaMode, bAutoMode, bVerifierLight = getStatus(dev, verbose=False)
        for line in os.popen('wmctrl -l').read().splitlines():
            if keywordCheckout.upper() in line.upper():
                if bInOut == 0x00: break
                print(f'--> found window title {keywordCheckout}, switch to check-out')
                sendStatusUpdate(dev, 0x00, bMediaMode, bAutoMode, bVerifierLight, trayIcon)
            elif keywordCheckin.upper() in line.upper():
                if bInOut == 0x01: break
                print(f'--> found window title {keywordCheckin}, switch to check-in')
                sendStatusUpdate(dev, 0x01, bMediaMode, bAutoMode, bVerifierLight, trayIcon)
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
        # initialize QT tray bar icon
        app = QtWidgets.QApplication(sys.argv)
        w = QtWidgets.QWidget()
        trayIcon = SystemTrayIcon(QtGui.QIcon(), w)
        trayIcon.show()

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
        t2 = Timer(1, autoModeChanger, [dev, keywordCheckout, keywordCheckin, trayIcon])
        t2.daemon = True
        t2.start()

        # start QT app (tray icon)
        sys.exit(app.exec_())

if(__name__ == '__main__'):
    main()
