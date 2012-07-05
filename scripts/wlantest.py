#!/usr/bin/python
##
## wlantest.py
##
## Script for automatic wireless testing using hostapd
##
## Author(s):
##  - Maxence VIALLON <mviallon@aldebaran-robotics.com>
##

import os
from time import sleep

from ConnmanClient import ConnmanClient
from Hostapd import Hostapd

class wlantest:

    def __init__(self):
        self.connman = ConnmanClient()
        self.hostapd = Hostapd()
    
    def wpa2(self):
        self.hostapd.reload("wpa2.conf")
        print("Hostap running mode wpa2")
        
        print("Scanning wifi ...")
        self.connman.scan()

        ServiceId = self.connman.getServiceId("wpa2rezo")

        print("Connecting to network ...")
        self.connman.setPassphrase("12345678")
        self.connman.connect(ServiceId)
         
        print("Checking network status ...")
        if self.connman.serviceisConnected(ServiceId):
            print "Success !"
        else:
            print "Fail"

        print("Disconnecting ...")
        self.connman.disconnect(ServiceId)

    def stop(self):
        self.hostapd.kill()

if (__name__ == "__main__"):
    
    # TODO : Start dhcp
    
    wlantest = wlantest()

    wlantest.wpa2()

    wlantest.stop()

