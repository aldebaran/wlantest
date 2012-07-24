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
import ConfigParser

from ConnmanClient import ConnmanClient
from Hostapd import Hostapd

class wlantest:

    def __init__(self):
        self.connman = ConnmanClient()
        self.hostapd = Hostapd()

    def run(self, file):
        #Reading test file
        config = ConfigParser.RawConfigParser()
        config.read(file)

        #Parsing file to dictionary
        dict = {}
        for section in config.sections():
            dict.update(config.items(section))

        #APConfig
        if dict['security'] == 'open':
            self.hostapd.open(dict['ssid'])
        elif dict['security'] == 'wep':
            self.hostapd.wep(dict['ssid'], dict['passphrase'])
        elif dict['security'] == 'wpa-psk':
            self.hostapd.wpa_psk(dict['ssid'], dict['passphrase'])
        elif dict['security'] == 'wpa2-psk':
            self.hostapd.wpa2_psk(dict['ssid'], dict['passphrase'])
        elif dict['security'] == 'wpa-eap':
            self.hostapd.wpa_eap(dict['ssid'])
            self.connman.setConfig(dict['ssid'], dict['method'], dict['phase2'])
        elif dict['security'] == 'wpa2-eap':
            self.hostapd.wpa2_eap(dict['ssid'])
            self.connman.setConfig(dict['ssid'], dict['method'], dict['phase2'])

        #Connecting
        if dict['type'] == 'manual':
            self.connman.scan()
            ServiceId = self.connman.getServiceId(dict['ssid'])
            self.connman.connect(ServiceId, dict['passphrase'], dict['identity'])

        elif dict['type'] == 'auto':
            pass

        #Testing
        if self.connman.getState(ServiceId) == dict['state']
            return True
        else:
            return False

        #Disconnecting
        self.connman.disconnect(ServiceId)

    def stop(self):
        self.hostapd.kill()

if (__name__ == "__main__"):

    # TODO : Start dhcp

    wlantest = wlantest()

    wlantest.run('test.conf')

#    wlantest.open("openrezo")
#
#    wlantest.wep("weprezo", "1234567891")
#
#    wlantest.wpa_psk("wparezo", "42424242")
#
#    wlantest.wpa2_psk("wpa2rezo", "12345678")
#
#    wlantest.wpa_eap(ssid = "peaprezo",\
#                    method = "peap",\
#                    identity = "maxence",\
#                    passphrase = "pipo")
#
#    wlantest.wpa_eap(ssid = "ttlsrezo",\
#                    method = "ttls",\
#                    identity = "maxence",\
#                    passphrase = "pipo")
#
#    wlantest.wpa2_eap(ssid = "peaprezo",\
#                    method = "peap",\
#                    identity = "maxence",\
#                    passphrase = "pipo")
#
#    wlantest.wpa2_eap(ssid = "ttlsrezo",\
#                    method = "ttls",\
#                    identity = "maxence",\
#                    passphrase = "pipo")

    wlantest.stop()

