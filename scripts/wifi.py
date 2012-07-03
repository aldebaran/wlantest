#!/usr/bin/python
##
## wifi.py
##
## Script for automatic wireless testing using hostapd
##
## Author(s):
##  - Maxence VIALLON <mviallon@aldebaran-robotics.com>
##

CONF_DIR = "/home/maxence/src/wlantest/hostap"

import os
from time import sleep

from ConnmanClient import ConnmanClient
from Hostapd import Hostapd

def mode_process(conf):
    hostapd.reload(conf)
    print("Hostap running mode "+mode+"!")
    
    print("Scanning wifi ...")
    connman.scan()
    
    # Delay for connman to autoconnect
    sleep(5)
    
    connman.serviceisConnected()
    
if (__name__ == "__main__"):
    
    # Listing of hostapd configuration files
    print ("Reading hostap directory ...")
    MODES = os.listdir(CONF_DIR) 
    print MODES
    
    # TODO : Start dhcp
    
    connman = ConnmanClient()
    hostapd = Hostapd()
    
    # Main loop
    for mode in MODES:
        mode_process(mode)

    # Killing Hostapd
    hostapd.kill()

