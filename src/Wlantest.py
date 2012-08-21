#!/usr/bin/python
##
## Wlantest.py
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
from time import sleep

CONF_DIR = '/etc/wlantest'
CONF_FILES = sorted(os.listdir(CONF_DIR))

RUN_DIR = '/var/run/wlantest'

from ConnmanClient import ConnmanClient
from Hostapd import Hostapd

class Wlantest:

    def __init__(self):

        try:
            os.mkdir(RUN_DIR)
        except OSError, e:
            print e

        self.connman = ConnmanClient()
        self.hostapd = Hostapd()

        self.resultFile = open(OUTPUT_FILE, 'w')

    def run(self, test):
        self.failflag = False
        config = getConfig(test)

        #APConfig
        self.hostapd.setConfig(security = config['AP']['security'], \
                            passphrase = config['AP']['passphrase'], \
                            identity = config['AP']['identity'], \
                            mode = config['AP']['mode'], \
                            channel = config['AP']['channel'], \
                            channelposition = config['AP']['channelposition'], \
                            ssid = config['AP']['ssid'], \
                            hidden = config['AP']['hidden'])

        #Connecting
        if 'manual' in config['Client']['mode']:

            # A minimalist provision must be provided for EAP
            if config['AP']['security'] in ('wpa-eap', 'wpa2-eap'):
                self.connman.setConfig(Name = config['AP']['ssid'], \
                                    EAP = config['AP']['method'], \
                                    Phase2 = config['AP']['phase2'])

            self.connman.scan()

            try:
                if config['AP']['hidden'] == 'true':
                    ServiceId = self.connman.getServiceId('hidden')
                else:
                    ServiceId = self.connman.getServiceId(config['AP']['ssid'])
            except IOError, e:
                print e
                self.failflag = True
            else:
                if config['AP']['security'] == 'open':
                    self.connman.connect(ServiceId, \
                                        name = config['AP']['ssid'])
                        
                elif config['AP']['security'] in ('wep', 'wpa-psk', 'wpa2-psk'):
                    self.connman.connect(ServiceId, \
                                        name = config['AP']['ssid'], \
                                        passphrase = config['Client']['passphrase'])

                elif config['AP']['security'] in ('wpa-eap', 'wpa2-eap'):
                    self.connman.connect(ServiceId, \
                                        name = config['AP']['ssid'], \
                                        passphrase = config['Client']['passphrase'], \
                                        identity = config['Client']['identity'])

                sleep(15)
                ServiceId = self.connman.getServiceId(config['AP']['ssid'])
                self.test(ServiceId, config['Result'])
                self.connman.disconnect(ServiceId)

        if 'auto' in config['Client']['mode']:
            # Reloading hostapd to allow the client to connect again
            self.hostapd.kill()
            sleep(15)
            self.hostapd.start()

            # For WPA-EAP, a full provision must be provided
            if config['AP']['security'] in ('wpa-eap', 'wpa2-eap'):
                if config['AP']['hidden'] == 'true':
                    self.connman.setConfig(Name = config['AP']['ssid'], \
                                        Hidden = config['AP']['hidden'], \
                                        EAP = config['AP']['method'], \
                                        Phase2 = config['AP']['phase2'], \
                                        Passphrase = config['Client']['passphrase'], \
                                        Identity = config['Client']['identity'])
                else:
                    self.connman.setConfig(Name = config['AP']['ssid'], \
                                        EAP = config['AP']['method'], \
                                        Phase2 = config['AP']['phase2'], \
                                        Passphrase = config['Client']['passphrase'], \
                                        Identity = config['Client']['identity'])

            self.connman.autoconnect()

            try:
                ServiceId = self.connman.getServiceId(config['AP']['ssid'])
            except IOError, e:
                print e
                self.failflag = True
            else:
                self.test(ServiceId, config['Result'])
                self.connman.disconnect(ServiceId)

        #Cleaning
        self.connman.clearConfig(config['AP']['ssid'])
        try:
            ServiceId = self.connman.getServiceId(config['AP']['ssid'])
        except IOError, e:
            print e
        else:
            if config['AP']['security'] in ('open', 'wep', 'wpa-psk', 'wpa2-psk'):
                self.connman.remove(ServiceId)

        #Output in logfile
        if self.failflag == True:
            self.resultFile.write('Test ' + config['Description']['id_test'] + '\t[Fail]\n')
        else:
            self.resultFile.write('Test ' + config['Description']['id_test'] + '\t[Ok]\n')

    def test(self, ServiceId, Result):
        if self.connman.getState(ServiceId) in Result['state'] \
                and str(self.connman.getConnectError()) in Result['error']:
            pass
        else:
            self.failflag = True

    def stop(self):
        self.hostapd.kill()
        self.resultFile.close()

def getConfig(test):
    """
    Method to parse a wlantest config file into a dictionnary
    """
    conf = {}

    #Reading test file
    config = ConfigParser.RawConfigParser()
    config.read(CONF_DIR + '/' + test)

    #Parsing file to dictionary
    for section in config.sections():
        d = {}
        for option in config.options(section):
            value = [v.strip() for v in config.get(section, option).split(',')]
            if len(value) == 1:
                if option == 'channel':
                    value = int(value[0])
                else:
                    value = value[0]
            d[option] = value
        conf[section] = d

    # id_test value not provided in configuration file
    conf['Description']['id_test'] = test[:test.rfind('.')]

    # Default values
    conf['AP'].setdefault('ssid', conf['Description']['id_test'])
    conf['AP'].setdefault('hidden', 'false')
    conf['AP'].setdefault('channelposition', '')
    conf['AP'].setdefault('identity', '')
    conf['AP'].setdefault('passphrase', '')

    return conf

def main():
    wlantest = Wlantest()
    for test in CONF_FILES:
        wlantest.run(test)
    wlantest.stop()
    
if (__name__ == "__main__"):
    main()
