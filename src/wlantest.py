#!/usr/bin/python
##
## wlantest.py
##
## Script for automatic wireless testing using hostapd
##
## Author(s):
##  - Maxence VIALLON <mviallon@aldebaran-robotics.com>
##

OUTPUT_FILE = '/var/log/wlantest.log'
AUTO_TIMEOUT = 120

import os
from time import sleep
import ConfigParser

CONF_DIR = '/etc/wlantest'
CONF_FILES = sorted(os.listdir(CONF_DIR))

from ConnmanClient import ConnmanClient
from Hostapd import Hostapd

class wlantest:

    def __init__(self):
        self.connman = ConnmanClient()
        self.hostapd = Hostapd()

        self.output = open(OUTPUT_FILE, 'w')

    def run(self, file):
        #Reading test file
        config = ConfigParser.RawConfigParser()
        config.read(CONF_DIR + '/' + file)

        #Parsing file to dictionaries
        Description = {}
        AP = {}
        Connection = {}
        Result = {}

        Description.update(config.items('Description'))
        AP.update(config.items('AP'))
        Connection.update(config.items('Connection'))
        Result.update(config.items('Result'))

        if not 'ssid' in AP:
            AP['ssid'] = Description['id_test']

        #APConfig
        if AP['security'] == 'open':
            self.hostapd.open(AP['ssid'])
        elif AP['security'] == 'wep':
            self.hostapd.wep(AP['ssid'], AP['passphrase'])
        elif AP['security'] == 'wpa-psk':
            self.hostapd.wpa_psk(AP['ssid'], AP['passphrase'])
        elif AP['security'] == 'wpa2-psk':
            self.hostapd.wpa2_psk(AP['ssid'], AP['passphrase'])
        elif AP['security'] == 'wpa-eap':
            self.hostapd.wpa_eap(AP['ssid'])
            self.connman.setConfig(Name = AP['ssid'], \
                                EAP = AP['method'], \
                                Phase2 = AP['phase2'])
        elif AP['security'] == 'wpa2-eap':
            self.hostapd.wpa2_eap(AP['ssid'])
            self.connman.setConfig(Name = AP['ssid'], \
                                EAP = AP['method'], \
                                Phase2 = AP['phase2'])

        #Connecting
        if Connection['type'] == 'manual':
            self.connman.scan()
            ServiceId = self.connman.getServiceId(AP['ssid'])
            if AP['security'] == 'open':
                self.connman.connect(ServiceId)
            elif AP['security'] in ('wep', 'wpa-psk', 'wpa2-psk'):
                self.connman.connect(ServiceId, \
                                    passphrase = Connection['passphrase'])
            elif AP['security'] in ('wpa-eap', 'wpa2-eap'):
                self.connman.connect(ServiceId, \
                                    passphrase = Connection['passphrase'], \
                                    identity = Connection['identity'])

        elif Connection['type'] == 'auto':
            if AP['security'] == 'open':
                self.connman.setConfig(Name = AP['ssid'])
            elif AP['security'] in ('wep', 'wpa-psk', 'wpa2-psk'):
                self.connman.setConfig(Name = AP['ssid'], \
                                    Passphrase = AP['passphrase'])
            elif AP['security'] in ('wpa-eap', 'wpa2-eap'):
                self.connman.setConfig(Name = AP['ssid'], \
                                    EAP = AP['method'], \
                                    Phase2 = AP['phase2'], \
                                    Passphrase = Connection['passphrase'], \
                                    Identity = Connection['identity'])
            sleep(120)
            ServiceId = self.connman.getServiceId(AP['ssid'])

        #Testing
        if self.connman.getState(ServiceId) == Result['state'] \
                and str(self.connman.getConnectError()) == Result['error']:
            self.output.write('Test ' + Description['id_test'] + '\t[Ok]\n')
        else:
            self.output.write('Test ' + Description['id_test'] + '\t[Fail]\n')

        #Disconnecting
        self.connman.disconnect(ServiceId)
        self.connman.clearConfig(AP['ssid'])
        self.connman.remove(ServiceId)

    def stop(self):
        self.hostapd.kill()
        self.output.close()

def main():
    mytest = wlantest()
    for file in CONF_FILES:
        mytest.run(file)
    mytest.stop()
    
if (__name__ == "__main__"):
    main()
