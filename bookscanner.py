#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
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
initcmd = config.get('init', None)
if(initcmd):
    print('Send init command:', initcmd)
    ser.write(initcmd.encode('ascii'))

# read barcodes from scanner and send to OS
requiredGoodReads = int(config.get('requiredgoodreads', 3))
currentGoodReads = 0
currentBarcode = ''
while True:
    barcode = ser.readline().decode('ascii').strip()
    if(barcode == currentBarcode):
        currentGoodReads += 1
    else:
        currentGoodReads = 0
    currentBarcode = barcode

    if(currentGoodReads == requiredGoodReads):
        print('Barcode:', barcode)
        try:
            import pyautogui
            pyautogui.typewrite(barcode)
            pyautogui.press('enter')
        except Exception as e:
            print('Unable to send keystrokes to desktop:', type(e), e)

    time.sleep(0.01)
