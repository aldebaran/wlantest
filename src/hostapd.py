#!/usr/bin/python
##
##  Hostapd client for wlantest
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
CONF_FILE = "/var/run/wlantest/hostapd.conf"
ENTROPY_FILE = "/var/run/wlantest/hostapd.entropy"

import subprocess
from time import sleep

class HostapdConfig:
    """
    Class to write conf file for hostapd
    """

    def __init__(self, interface):
        self.config = open (CONF_FILE, "w+")
        # Set shared settings
        self.set("interface", interface)
        self.set("driver", 'nl80211')

    def set(self, key, value):
        self.config.write("%s=%s\n" %(key,value))

    def close(self):
        self.config.close()

class Hostapd:
    """
    Class to manage hostapd
    """

    def __init__(self, interface, nas_ip, radius_ip, radius_port, radius_secret):
        self.interface = interface
        self.nas_ip = nas_ip
        self.radius_ip = radius_ip
        self.radius_port = radius_port
        self.radius_secret = radius_secret

        # Set default config to let hostapd start
        self.setDefaultConfig()

        self.cmd = ["hostapd", CONF_FILE, "-e", ENTROPY_FILE]
        self.start()

    def setDefaultConfig(self):
        config = HostapdConfig(self.interface)
        config.set("channel", "1")
        config.set("hw_mode", "g")
        config.close()

    def setConfig(self, security, passphrase, identity, mode, channel, channelposition, ssid, hidden):
        config = HostapdConfig(self.interface)

        # Radio settings
        config.set("ssid", ssid)
        if hidden == 'true':
            config.set("ignore_broadcast_ssid", "1")

        config.set("channel", str(channel))

        if mode in ('a', 'b' ,'g'):
            config.set("hw_mode", mode)
        elif mode == 'n':
            config.set("ieee80211n", "1")

            if channel in range(1,14):
                config.set("hw_mode", "g")
                config.set("ht_capab", "[GF]")
            elif channel in range (36,48):
                config.set("hw_mode", "a")
                if channelposition == 'upper':
                    config.set("ht_capab", "[GF][HT40-]")
                elif channelposition == 'lower':
                    config.set("ht_capab", "[GF][HT40+]")

        elif mode == 'gn':
            config.set("ieee80211n", "1")
            config.set("hw_mode", "g")

        # Security settings
        if security == 'wep':
            config.set("wep_default_key", "0")
            config.set("wep_key0", passphrase)

        elif security == 'wpa-psk':
            config.set("wpa", "1")
            try:
                passphrase = passphrase.split('"')[1]
                config.set("wpa_passphrase", passphrase)
            except IndexError:
                config.set("wpa_psk", passphrase)
            config.set("wpa_key_mgmt", "WPA-PSK")
            config.set("wpa_pairwise", "TKIP")

        elif security == 'wpa2-psk':
            config.set("wpa", "2")
            try:
                passphrase = passphrase.split('"')[1]
                config.set("wpa_passphrase", passphrase)
            except IndexError:
                config.set("wpa_psk", passphrase)
            config.set("wpa_key_mgmt", "WPA-PSK")
            config.set("wpa_pairwise", "CCMP")

        elif security == 'wpa-eap':
            config.set("ieee8021x", "1")
            config.set("own_ip_addr", self.nas_ip)
            config.set("auth_server_addr", self.radius_ip)
            config.set("auth_server_port", self.radius_port)
            config.set("auth_server_shared_secret", self.radius_secret)
            config.set("wpa", "1")
            config.set("wpa_key_mgmt", "WPA-EAP")
            config.set("wpa_pairwise", "TKIP")

        elif security == 'wpa2-eap':
            config.set("ieee8021x", "1")
            config.set("own_ip_addr", self.nas_ip)
            config.set("auth_server_addr", self.radius_ip)
            config.set("auth_server_port", self.radius_port)
            config.set("auth_server_shared_secret", self.radius_secret)
            config.set("wpa", "2")
            config.set("wpa_key_mgmt", "WPA-EAP")
            config.set("wpa_pairwise", "CCMP")

        config.close()
        self.reload()

    def reload(self):
       # No SIGHUP to reload because of known issues (bug 396)
       # os.kill(self.proc.pid, signal.SIGHUP)
        self.kill()
        self.start()

    def start(self):
        self.proc = subprocess.Popen(self.cmd)
        sleep(5)

    def kill(self):
        self.proc.terminate()
        self.proc.wait()

if (__name__ == "__main__"):

    myhost = Hostapd()
    myhost.setConfig(security = 'wpa2-psk', \
                    mode = 'g', \
                    channel = 4, \
                    ssid = 'serious_ssid', \
                    passphrase = '12345678')
