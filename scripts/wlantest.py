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
    
    def wpa_psk(self, ssid, passphrase):
        self.hostapd.wpa_psk(ssid, passphrase)
        print("Hostap running mode wpa/psk")

        self.test(ssid, passphrase)

    def wpa2_psk(self, ssid, passphrase):
        self.hostapd.wpa2_psk(ssid, passphrase)
        print("Hostap running mode wpa2/psk")

        self.test(ssid, passphrase)
        
    def wpa_eap(self, ssid, identity, passphrase):
        self.hostapd.wpa_eap(ssid)
        print("Hostap running mode wpa/eap")
        
        self.connman.setConfig(ssid, "peap", "MSCHAPV2")

        self.test(ssid, passphrase, identity)

    def wpa2_eap(self, ssid, identity, passphrase):
        self.hostapd.wpa2_eap(ssid)
        print("Hostap running mode wpa2/eap")
        
        self.connman.setConfig(ssid, "peap", "MSCHAPV2")

        self.test(ssid, passphrase, identity)

    def test(self, ssid, passphrase, identity = None):

        print("Scanning wifi ...")
        self.connman.scan()

        print("Connecting to network ...")
        ServiceId = self.connman.getServiceId(ssid)

        self.connman.setCredentials(passphrase = passphrase, identity = identity)
        self.connman.connect(ServiceId)
    
        print("Checking network status ...")
        if self.connman.serviceisConnected(ServiceId):
            print "\033[92m[Ok]\033[0m"
        else:
            print "\033[91m[Err]\033[0m"

        print("Disconnecting ...")
        self.connman.disconnect(ServiceId)

    def stop(self):
        self.hostapd.kill()

if (__name__ == "__main__"):
    
    # TODO : Start dhcp

    wlantest = wlantest()
    
    wlantest.open("openrezo")

    wlantest.wep("weprezo", "1234567891")

    wlantest.wpa_psk("wparezo", "42424242")

    wlantest.wpa2_psk("wpa2rezo", "12345678")

    wlantest.wpa_eap("peaprezo", "maxence", "pipo")

    wlantest.wpa2_eap("peaprezo", "maxence", "pipo")

    wlantest.stop()
    
