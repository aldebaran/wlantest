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
        if not 'hidden' in AP:
            AP['hidden'] = 'false'

        #APConfig
        if AP['security'] == 'open':
            self.hostapd.open(mode = AP['mode'], \
                            chan = AP['channel'], \
                            ssid = AP['ssid'], \
                            hidden = AP['hidden'])
        elif AP['security'] == 'wep':
            self.hostapd.wep(mode = AP['mode'], \
                            chan = AP['channel'], \
                            ssid = AP['ssid'], \
                            hidden = AP['hidden'], \
                            passphrase = AP['passphrase'])
        elif AP['security'] == 'wpa-psk':
            self.hostapd.wpa_psk(mode = AP['mode'], \
                                chan = AP['channel'], \
                                ssid = AP['ssid'], \
                                hidden = AP['hidden'], \
                                passphrase = AP['passphrase'])
        elif AP['security'] == 'wpa2-psk':
            self.hostapd.wpa2_psk(mode = AP['mode'], \
                                chan = AP['channel'], \
                                ssid = AP['ssid'], \
                                hidden = AP['hidden'], \
                                passphrase = AP['passphrase'])
        elif AP['security'] == 'wpa-eap':
            self.hostapd.wpa_eap(mode = AP['mode'], \
                                chan = AP['channel'], \
                                ssid = AP['ssid'], \
                                hidden = AP['hidden'])
            self.connman.setConfig(Name = AP['ssid'], \
                                EAP = AP['method'], \
                                Phase2 = AP['phase2'])
        elif AP['security'] == 'wpa2-eap':
            self.hostapd.wpa2_eap(mode = AP['mode'], \
                                chan = AP['channel'], \
                                ssid = AP['ssid'], \
                                hidden = AP['hidden'])
            self.connman.setConfig(Name = AP['ssid'], \
                                EAP = AP['method'], \
                                Phase2 = AP['phase2'])

        #Connecting
        if Connection['type'] == 'manual':
            self.connman.scan()
            if AP['hidden'] == 'true':
                ServiceId = self.connman.getServiceId('hidden')
                if AP['security'] == 'open':
                    self.connman.connect(ServiceId, \
                                        name = AP['ssid'])
                elif AP['security'] in ('wep', 'wpa-psk', 'wpa2-psk'):
                    self.connman.connect(ServiceId, \
                                        name = AP['ssid'], \
                                        passphrase = Connection['passphrase'])
                elif AP['security'] in ('wpa-eap', 'wpa2-eap'):
                    self.connman.connect(ServiceId, \
                                        name = AP['ssid'], \
                                        passphrase = Connection['passphrase'], \
                                        identity = Connection['identity'])
            else:
                ServiceId = self.connman.getServiceId(AP['ssid'])
                if AP['security'] == 'open':
                    self.connman.connect(ServiceId, \
                                        name = AP['ssid'])
                elif AP['security'] in ('wep', 'wpa-psk', 'wpa2-psk'):
                    self.connman.connect(ServiceId, \
                                        name = AP['ssid'], \
                                        passphrase = Connection['passphrase'])
                elif AP['security'] in ('wpa-eap', 'wpa2-eap'):
                    self.connman.connect(ServiceId, \
                                        name = AP['ssid'], \
                                        passphrase = Connection['passphrase'], \
                                        identity = Connection['identity'])

        elif Connection['type'] == 'auto':
            if AP['hidden'] == 'true':
                if AP['security'] == 'open':
                    self.connman.setConfig(Name = AP['ssid'], \
                                        Hidden = AP['hidden'])
                elif AP['security'] in ('wep', 'wpa-psk', 'wpa2-psk'):
                    self.connman.setConfig(Name = AP['ssid'], \
                                        Hidden = AP['hidden'], \
                                        Passphrase = Connection['passphrase'])
                elif AP['security'] in ('wpa-eap', 'wpa2-eap'):
                    self.connman.setConfig(Name = AP['ssid'], \
                                        Hidden = AP['hidden'], \
                                        EAP = AP['method'], \
                                        Phase2 = AP['phase2'], \
                                        Passphrase = Connection['passphrase'], \
                                        Identity = Connection['identity'])
            else:
                if AP['security'] == 'open':
                    self.connman.setConfig(Name = AP['ssid'])
                elif AP['security'] in ('wep', 'wpa-psk', 'wpa2-psk'):
                    self.connman.setConfig(Name = AP['ssid'], \
                                        Passphrase = Connection['passphrase'])
                elif AP['security'] in ('wpa-eap', 'wpa2-eap'):
                    self.connman.setConfig(Name = AP['ssid'], \
                                        EAP = AP['method'], \
                                        Phase2 = AP['phase2'], \
                                        Passphrase = Connection['passphrase'], \
                                        Identity = Connection['identity'])

            self.connman.autoconnect()

        #Testing
        ServiceId = self.connman.getServiceId(AP['ssid'])
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
