#!/usr/bin/python
##
##  Automatic wireless testing for Connman
##
##  Copyright (C) 2012-2013  Aldebaran Robotics. All rights reserved.
##
##  This program is free software; you can redistribute it and/or modify
##  it under the terms of the GNU General Public License version 2 as
##  published by the Free Software Foundation.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with this program; if not, write to the Free Software
##  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
##
import os
from time import sleep

import ConfigParser
from collections import namedtuple

MAIN_CONF = '/etc/wlantest/main.conf'
CONF_DIR = '/etc/wlantest/cfg'
CONF_FILES = sorted(os.listdir(CONF_DIR))

RUN_DIR = '/var/run/wlantest'
OUTPUT_FILE = '/var/log/wlantest.log'

from connmanclient import ConnmanClient
from hostapd import Hostapd

wlantest_settings = namedtuple('wlantest_settings', ['ap_iface', 'nas_ip', 'radius_ip', \
    'radius_port', 'radius_secret', 'autoconnect_timeout'])

class Wlantest:

    def __init__(self, config_file):

        try:
            os.mkdir(RUN_DIR)
        except OSError, e:
            print e

        settings = parseMainConfig(config_file)

        self.connman = ConnmanClient(autoconnect_timeout = settings.autoconnect_timeout)
        self.hostapd = Hostapd(interface = settings.ap_iface,
                                nas_ip = settings.nas_ip,
                                radius_ip = settings.radius_ip,
                                radius_port = settings.radius_port,
                                radius_secret = settings.radius_secret)

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

def loadConfig(configfile):
    """
    Method to load a config file into ConfigParser
    """
    config = ConfigParser.RawConfigParser()
    config.read(configfile)
    return config

def getConfig(test):
    """
    Method to parse a wlantest config file into a dictionnary
    """
    conf = {}

    config = loadConfig(CONF_DIR + '/' + test)

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

def parseMainConfig(mainconfig):
    """
    Method to parse wlantest main config
    """
    config = loadConfig(mainconfig)

    try:
        ap_iface = config.get('general', 'APInterface')
    except ConfigParser.NoOptionError, e:
        ap_iface = 'wlan0'
        print e
    try:
        nas_ip = config.get('general', 'NAS_IP')
    except ConfigParser.NoOptionError, e:
        nas_ip = '192.168.2.4'
        print e
    try:
        radius_ip = config.get('general', 'RADIUS_IP')
    except ConfigParser.NoOptionError, e:
        radius_ip = '192.168.2.3'
        print e
    try:
        radius_port = config.get('general', 'RADIUS_PORT')
    except ConfigParser.NoOptionError, e:
        radius_port = '1812'
        print e
    try:
        radius_secret = config.get('general', 'RADIUS_SECRET')
    except ConfigParser.NoOptionError, e:
        radius_secret = 'testing123'
        print e
    try:
        autoconnect_timeout = int(config.get('general', 'AutoconnectTimeout'))
    except ConfigParser.NoOptionError, e:
        autoconnect_timeout = 90
        print e

    settings = wlantest_settings(ap_iface, nas_ip, radius_ip, radius_port, radius_secret, autoconnect_timeout)

    return settings

def main():
    wlantest = Wlantest(MAIN_CONF)

    for test in CONF_FILES:
        wlantest.run(test)

    wlantest.stop()

if (__name__ == "__main__"):
    main()
