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
import socket
import fcntl
import struct

import ConfigParser
from collections import namedtuple

MAIN_CONF = '/etc/wlantest/main.conf'
CONF_DIR = '/etc/wlantest/cfg'
CONF_FILES = os.listdir(CONF_DIR)

RUN_DIR = '/var/run/wlantest'
OUTPUT_FILE = '/var/log/wlantest.log'

from connmanclient import ConnmanClient
from hostapd import Hostapd

wlantest_settings = namedtuple('wlantest_settings', ['sta_iface', 'ap_iface', 'nas_ip', \
        'radius_ip', 'radius_port', 'radius_secret', 'autoconnect_timeout'])

class Wlantest:

    def __init__(self, config_file):

        try:
            os.mkdir(RUN_DIR)
        except OSError, e:
            print e

        self.settings = parseMainConfig(config_file)

        self.connman = ConnmanClient(autoconnect_timeout = self.settings.autoconnect_timeout)
        self.hostapd = Hostapd(interface = self.settings.ap_iface,
                                nas_ip = self.settings.nas_ip,
                                radius_ip = self.settings.radius_ip,
                                radius_port = self.settings.radius_port,
                                radius_secret = self.settings.radius_secret)

        self.ap_mac_address = get_mac_address(self.settings.sta_iface)

        self.resultFile = open(OUTPUT_FILE, 'w')

    def run(self, test):
        self.failflag = False
        self.config = getConfig(test)

        #Configure AP
        self.hostapd.setConfig(security = self.config['AP']['security'], \
                            passphrase = self.config['AP']['passphrase'], \
                            identity = self.config['AP']['identity'], \
                            mode = self.config['AP']['mode'], \
                            channel = self.config['AP']['channel'], \
                            channelposition = self.config['AP']['channelposition'], \
                            ssid = self.config['AP']['ssid'], \
                            hidden = self.config['AP']['hidden'])

        #Test connectivity
        if 'manual' in self.config['Client']['mode']:
            self.manualConnect()

        if 'auto' in self.config['Client']['mode']:
            self.autoConnect()

        #Cleaning
        self.clean()

        #Output in logfile
        if self.failflag == True:
            self.resultFile.write('Test ' + self.config['Description']['id_test'] + '\t[Fail]\n')
        else:
            self.resultFile.write('Test ' + self.config['Description']['id_test'] + '\t[Ok]\n')

    def clean(self):
        self.connman.clearConfig(self.config['AP']['ssid'])
        try:
            if self.config['AP']['security'] == 'open':
                serviceId = self.connman.getServiceId(name = self.config['AP']['ssid'], \
                                                      technology = 'wifi', \
                                                      security = 'none',
                                                      mac_address = self.ap_mac_address)
                self.connman.remove(serviceId)
            elif self.config['AP']['security'] in ('wep', 'wpa-psk', 'wpa2-psk'):
                serviceId = self.connman.getServiceId(name = self.config['AP']['ssid'], \
                                                      technology = 'wifi', \
                                                      security = 'psk',
                                                      mac_address = self.ap_mac_address)
                self.connman.remove(serviceId)
        except IOError, e:
            print e

    def manualConnect(self):
        # A minimalist provision must be provided for EAP
        if self.config['AP']['security'] in ('wpa-eap', 'wpa2-eap'):
            self.connman.setConfig(Name = self.config['AP']['ssid'], \
                                EAP = self.config['AP']['method'], \
                                Phase2 = self.config['AP']['phase2'])

        self.connman.scan()

        if self.config['AP']['hidden'] == 'true':
            name = None
        else:
            name = self.config['AP']['ssid']

        #Next steps depends on security
        try:
            if self.config['AP']['security'] == 'open':
                serviceId = self.connman.getServiceId(name = name, \
                                                      technology = 'wifi', \
                                                      security = 'none', \
                                                      mac_address = self.ap_mac_address)
                self.connman.connect(serviceId, \
                                     name = self.config['AP']['ssid'])
                sleep(15)
                serviceId = self.connman.getServiceId(name = self.config['AP']['ssid'], \
                                                        technology = 'wifi', \
                                                        security = 'none',
                                                        mac_address = self.ap_mac_address)

            if self.config['AP']['security'] == 'wep':
                serviceId = self.connman.getServiceId(name = name, \
                                                      technology = 'wifi', \
                                                      security = 'wep', \
                                                      mac_address = self.ap_mac_address)
                self.connman.connect(serviceId, \
                                     name = self.config['AP']['ssid'], \
                                     passphrase = self.config['Client']['passphrase'])
                sleep(15)
                serviceId = self.connman.getServiceId(name = self.config['AP']['ssid'], \
                                                        technology = 'wifi', \
                                                        security = 'wep',
                                                        mac_address = self.ap_mac_address)

            elif self.config['AP']['security'] in ('wpa-psk', 'wpa2-psk'):
                serviceId = self.connman.getServiceId(name = name, \
                                                      technology = 'wifi', \
                                                      security = 'psk', \
                                                      mac_address = self.ap_mac_address)
                self.connman.connect(serviceId, \
                                     name = self.config['AP']['ssid'], \
                                     passphrase = self.config['Client']['passphrase'])
                sleep(15)
                serviceId = self.connman.getServiceId(name = self.config['AP']['ssid'], \
                                                        technology = 'wifi', \
                                                        security = 'psk',
                                                        mac_address = self.ap_mac_address)

            elif self.config['AP']['security'] in ('wpa-eap', 'wpa2-eap'):
                serviceId = self.connman.getServiceId(name = name, \
                                                      technology = 'wifi', \
                                                      security = 'ieee8021x', \
                                                      mac_address = self.ap_mac_address)
                self.connman.connect(serviceId, \
                                     name = self.config['AP']['ssid'], \
                                     passphrase = self.config['Client']['passphrase'], \
                                     identity = self.config['Client']['identity'])
                sleep(15)
                serviceId = self.connman.getServiceId(name = self.config['AP']['ssid'], \
                                                        technology = 'wifi', \
                                                        security = 'ieee8021x',
                                                        mac_address = self.ap_mac_address)

        except IOError, e:
           print e
           self.failflag = True
        else:
            self.test(serviceId, self.config['Result'])
            self.connman.disconnect(serviceId)

    def autoConnect(self):
        # Reloading hostapd to allow the client to connect again
        self.hostapd.kill()
        sleep(15)
        self.hostapd.start()

        # For WPA-EAP, a full provision must be provided
        if self.config['AP']['security'] in ('wpa-eap', 'wpa2-eap'):
            if self.config['AP']['hidden'] == 'true':
                self.connman.setConfig(Name = self.config['AP']['ssid'], \
                                    Hidden = self.config['AP']['hidden'], \
                                    EAP = self.config['AP']['method'], \
                                    Phase2 = self.config['AP']['phase2'], \
                                    Passphrase = self.config['Client']['passphrase'], \
                                    Identity = self.config['Client']['identity'])
            else:
                self.connman.setConfig(Name = self.config['AP']['ssid'], \
                                    EAP = self.config['AP']['method'], \
                                    Phase2 = self.config['AP']['phase2'], \
                                    Passphrase = self.config['Client']['passphrase'], \
                                    Identity = self.config['Client']['identity'])

        self.connman.autoconnect()

        try:
            if self.config['AP']['security'] == 'open':
                serviceId = self.connman.getServiceId(name = self.config['AP']['ssid'], \
                                                      technology = 'wifi', \
                                                      security = 'none', \
                                                      mac_address = self.ap_mac_address)

            if self.config['AP']['security'] == 'wep':
                serviceId = self.connman.getServiceId(name = self.config['AP']['ssid'], \
                                                      technology = 'wifi', \
                                                      security = 'wep', \
                                                      mac_address = self.ap_mac_address)

            elif self.config['AP']['security'] in ('wep', 'wpa-psk', 'wpa2-psk'):
                serviceId = self.connman.getServiceId(name = self.config['AP']['ssid'], \
                                                      technology = 'wifi', \
                                                      security = 'psk', \
                                                      mac_address = self.ap_mac_address)

            elif self.config['AP']['security'] in ('wpa-eap', 'wpa2-eap'):
                serviceId = self.connman.getServiceId(name = self.config['AP']['ssid'], \
                                                      technology = 'wifi', \
                                                      security = 'ieee8021x', \
                                                      mac_address = self.ap_mac_address)

        except IOError, e:
           print e
           self.failflag = True
        else:
            self.test(serviceId, self.config['Result'])
            self.connman.disconnect(serviceId)

    def test(self, serviceId, Result):
        if self.connman.getState(serviceId) in Result['state'] \
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
        sta_iface = config.get('general', 'STAInterface')
    except ConfigParser.NoOptionError, e:
        sta_iface = 'wlan0'
        print e
    try:
        ap_iface = config.get('general', 'APInterface')
    except ConfigParser.NoOptionError, e:
        ap_iface = 'wlan1'
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

    settings = wlantest_settings(sta_iface, ap_iface, nas_ip, radius_ip, radius_port, radius_secret, autoconnect_timeout)

    return settings

def get_mac_address(ifname, default = None):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
        return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1].upper()
    except:
        return default

def main():
    wlantest = Wlantest(MAIN_CONF)

    for test in CONF_FILES:
        wlantest.run(test)

    wlantest.stop()

if (__name__ == "__main__"):
    main()
