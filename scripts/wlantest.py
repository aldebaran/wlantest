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

from ConnmanClient import ConnmanClient
from Hostapd import Hostapd

class wlantest:

    def __init__(self):
        self.connman = ConnmanClient()
        self.hostapd = Hostapd()

    def open(self, ssid):
        self.hostapd.open(ssid)
        print("Hostap running mode open")

        self.test(ssid, None)
    
    def wep(self, ssid, passphrase):
        self.hostapd.wep(ssid, passphrase)
        print("Hostap running mode wep")

        self.test(ssid, passphrase)
    
    def wpa2(self, ssid, passphrase):
        self.hostapd.wpa2(ssid, passphrase)
        print("Hostap running mode wpa2")

        self.test(ssid, passphrase)
        
    def wpa(self, ssid, passphrase):
        self.hostapd.wpa(ssid, passphrase)
        print("Hostap running mode wpa")

        self.test(ssid, passphrase)

    def wpa_eap(self, ssid, identity, passphrase):
        self.hostapd.eapwpa(ssid)
        print("Hostap running mode eap/wpa")
        
        # TODO : Write new section in connman.config

        self.test(self, ssid, passphrase,identity)

    def test(self, ssid, passphrase, identity = None):

        print("Scanning wifi ...")
        self.connman.scan()

        print("Connecting to network ...")
        ServiceId = self.connman.getServiceId(ssid)

        self.connman.setCredentials(passphrase = passphrase, identity = identity)
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
    
    wlantest.open("openrezo")

    wlantest.wep("weprezo", "1234567891")

    wlantest.wpa2("wpa2rezo", "12345678")

    wlantest.wpa("wparezo", "42424242")

    wlantest.stop()
    
