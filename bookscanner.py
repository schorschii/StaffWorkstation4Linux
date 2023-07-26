#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from threading import Timer
import configparser
import serial
import time
import os


# read config
config = {}
configParser = configparser.ConfigParser()
configParser.read(str(Path.home())+'/.config/staffworkstation4linux.ini')
if(configParser.has_section('scanner')): config = dict(configParser.items('scanner'))

# open serial port
ser = serial.Serial(
    config.get('port', '/dev/ttyS0'),
    int(config.get('rate', 9600)),
)
print('Connected to:', ser.name)

# initialize scanner commands
initcmd = config.get('initcmd', '<Kr1,0,0,8,10><Kg1><H><A>')
if(initcmd):
    print('Send init command:', initcmd)
    ser.write(initcmd.encode('ascii'))

# read barcodes from scanner and send to OS
sleepcmd = config.get('sleepcmd', '<I>')
wakeupcmd = config.get('wakeupcmd', '<H>')
sleeptime = float(config.get('sleep', 1.5))
t = None

def wakeup():
    #print('wakeup!')
    t = None
    ser.write(wakeupcmd.encode('ascii'))

while True:
    barcode = ser.readline().decode('ascii').strip()

    if(sleeptime):
        #print('sleeping', sleeptime)
        ser.write(sleepcmd.encode('ascii'))
        if(not t or not t.is_alive()):
            t = Timer(sleeptime, wakeup)
            t.start()

    print('Barcode:', barcode)
    try:
        import pyautogui
        pyautogui.typewrite(barcode)
        pyautogui.press('enter')
    except Exception as e:
        print('Unable to send keystrokes to desktop:', type(e), e)

    time.sleep(0.01)
