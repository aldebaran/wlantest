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

        self.failflag = False
        d = getConfig(file)

        #APConfig
        if d['AP']['security'] == 'open':
            self.hostapd.open(mode = d['AP']['mode'], \
                            chan = d['AP']['channel'], \
                            ssid = d['AP']['ssid'], \
                            hidden = d['AP']['hidden'])
        elif d['AP']['security'] == 'wep':
            self.hostapd.wep(mode = d['AP']['mode'], \
                            chan = d['AP']['channel'], \
                            ssid = d['AP']['ssid'], \
                            hidden = d['AP']['hidden'], \
                            passphrase = d['AP']['passphrase'])
        elif d['AP']['security'] == 'wpa-psk':
            self.hostapd.wpa_psk(mode = d['AP']['mode'], \
                                chan = d['AP']['channel'], \
                                ssid = d['AP']['ssid'], \
                                hidden = d['AP']['hidden'], \
                                passphrase = d['AP']['passphrase'])
        elif d['AP']['security'] == 'wpa2-psk':
            self.hostapd.wpa2_psk(mode = d['AP']['mode'], \
                                chan = d['AP']['channel'], \
                                ssid = d['AP']['ssid'], \
                                hidden = d['AP']['hidden'], \
                                passphrase = d['AP']['passphrase'])
        elif d['AP']['security'] == 'wpa-eap':
            self.hostapd.wpa_eap(mode = d['AP']['mode'], \
                                chan = d['AP']['channel'], \
                                ssid = d['AP']['ssid'], \
                                hidden = d['AP']['hidden'])
            self.connman.setConfig(Name = d['AP']['ssid'], \
                                EAP = d['AP']['method'], \
                                Phase2 = d['AP']['phase2'])
        elif d['AP']['security'] == 'wpa2-eap':
            self.hostapd.wpa2_eap(mode = d['AP']['mode'], \
                                chan = d['AP']['channel'], \
                                ssid = d['AP']['ssid'], \
                                hidden = d['AP']['hidden'])
            self.connman.setConfig(Name = d['AP']['ssid'], \
                                EAP = d['AP']['method'], \
                                Phase2 = d['AP']['phase2'])

        #Connecting
        if 'manual' in d['Client']['mode']:
            self.connman.scan()

            try:
                if d['AP']['hidden'] == 'true':
                    ServiceId = self.connman.getServiceId('hidden')
                else:
                    ServiceId = self.connman.getServiceId(d['AP']['ssid'])
            except IOError, e:
                print e
                self.failflag = True
            else:
                if d['AP']['security'] == 'open':
                    self.connman.connect(ServiceId, \
                                        name = d['AP']['ssid'])
                elif d['AP']['security'] in ('wep', 'wpa-psk', 'wpa2-psk'):
                    self.connman.connect(ServiceId, \
                                        name = d['AP']['ssid'], \
                                        passphrase = d['Client']['passphrase'])
                elif d['AP']['security'] in ('wpa-eap', 'wpa2-eap'):
                    self.connman.connect(ServiceId, \
                                        name = d['AP']['ssid'], \
                                        passphrase = d['Client']['passphrase'], \
                                        identity = d['Client']['identity'])

                ServiceId = self.connman.getServiceId(d['AP']['ssid'])
                self.test(ServiceId, d['Result'])
                self.connman.disconnect(ServiceId)

        if 'auto' in d['Client']['mode']:
            # Reloading hostapd to allow the client to connect again
            self.hostapd.reload(45)
            self.connman.autoconnect()

            try:
                ServiceId = self.connman.getServiceId(d['AP']['ssid'])
            except IOError, e:
                print e
                self.failflag = True
            else:
                self.test(ServiceId, d['Result'])
                self.connman.disconnect(ServiceId)

        if 'provision' in d['Client']['mode']:
            if d['AP']['hidden'] == 'true':
                if d['AP']['security'] == 'open':
                    self.connman.setConfig(Name = d['AP']['ssid'], \
                                        Hidden = d['AP']['hidden'])
                elif d['AP']['security'] in ('wep', 'wpa-psk', 'wpa2-psk'):
                    self.connman.setConfig(Name = d['AP']['ssid'], \
                                        Hidden = d['AP']['hidden'], \
                                        Passphrase = d['Client']['passphrase'])
                elif d['AP']['security'] in ('wpa-eap', 'wpa2-eap'):
                    self.connman.setConfig(Name = d['AP']['ssid'], \
                                        Hidden = d['AP']['hidden'], \
                                        EAP = d['AP']['method'], \
                                        Phase2 = d['AP']['phase2'], \
                                        Passphrase = d['Client']['passphrase'], \
                                        Identity = d['Client']['identity'])
            else:
                if d['AP']['security'] == 'open':
                    self.connman.setConfig(Name = d['AP']['ssid'])
                elif d['AP']['security'] in ('wep', 'wpa-psk', 'wpa2-psk'):
                    self.connman.setConfig(Name = d['AP']['ssid'], \
                                        Passphrase = d['Client']['passphrase'])
                elif d['AP']['security'] in ('wpa-eap', 'wpa2-eap'):
                    self.connman.setConfig(Name = d['AP']['ssid'], \
                                        EAP = d['AP']['method'], \
                                        Phase2 = d['AP']['phase2'], \
                                        Passphrase = d['Client']['passphrase'], \
                                        Identity = d['Client']['identity'])

            self.connman.autoconnect()
            try:
                ServiceId = self.connman.getServiceId(d['AP']['ssid'])
            except IOError, e:
                print e
                self.failflag = True
            else:
                self.test(ServiceId, d['Result'])
                self.connman.disconnect(ServiceId)

        #Cleaning
        self.connman.clearConfig(d['AP']['ssid'])
        try:
            ServiceId = self.connman.getServiceId(d['AP']['ssid'])
        except IOError, e:
            print e
        else:
            if d['AP']['security'] in ('open', 'wep', 'wpa-psk', 'wpa2-psk'):
                self.connman.remove(ServiceId)

        #Output in logfile
        if self.failflag == True:
            self.output.write('Test ' + d['Description']['id_test'] + '\t[Fail]\n')
        else:
            self.output.write('Test ' + d['Description']['id_test'] + '\t[Ok]\n')

    def test(self, ServiceId, Result):
        if self.connman.getState(ServiceId) in Result['state'] \
                and str(self.connman.getConnectError()) in Result['error']:
            pass
        else:
            self.failflag = True

    def stop(self):
        self.hostapd.kill()
        self.output.close()

def getConfig(file):
    """
    Method to parse a config file into a dictionnary
    """
    conf = {}

    #Reading test file
    config = ConfigParser.RawConfigParser()
    config.read(CONF_DIR + '/' + file)

    #Parsing file to dictionary
    for section in config.sections():
        d = {}
        for option in config.options(section):
            value = [v.strip() for v in config.get(section, option).split(',')]
            if len(value) == 1:
                value = value[0]
            d[option] = value
        conf[section] = d

    # id_test value not provided in configuration filie
    conf['Description']['id_test'] = file[:file.rfind('.')]

    # Default values
    conf['AP'].setdefault('ssid', conf['Description']['id_test'])
    conf['AP'].setdefault('hidden', 'false')

    return conf

def main():
    mytest = wlantest()
    for file in CONF_FILES:
        mytest.run(file)
    mytest.stop()
    
if (__name__ == "__main__"):
    main()
