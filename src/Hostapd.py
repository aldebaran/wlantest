#!/usr/bin/python
##
## Hostapd.py
##
## Author(s):
##  - Maxence VIALLON <mviallon@aldebaran-robotics.com>
##

CONF_FILE = "/etc/hostapd.conf"
IFACE = "wlan1"
DRIVER = "nl80211"

NAS_IP = "192.168.2.2"
RADIUS_IP = "192.168.2.3"
RADIUS_PORT = "1812"
RADIUS_SECRET = "testing123"

import subprocess
from time import sleep

class HostapdConfig:
    """
    Class to write conf file for hostapd
    """

    def __init__(self):
        self.config = open (CONF_FILE, "w+")
        # Set shared settings
        self.set("interface", IFACE)
        self.set("driver", DRIVER)

    def set(self, key, value):
        self.config.write("%s=%s\n" %(key,value))

    def close(self):
        self.config.close()

class Hostapd:
    """
    Class to manage hostapd
    """

    def __init__(self):
        # Set default config to let hostapd start
        self.setDefaultConfig()

        self.cmd = ["hostapd", CONF_FILE]
        self.start()

    def setDefaultConfig(self):
        config = HostapdConfig()
        config.set("channel", "1")
        config.set("hw_mode", "g")
        config.close()

    def setConfig(self, security, passphrase, identity, mode, channel, channelposition, ssid, hidden):
        config = HostapdConfig()

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
            config.set("own_ip_addr", NAS_IP)
            config.set("auth_server_addr", RADIUS_IP)
            config.set("auth_server_port", RADIUS_PORT)
            config.set("auth_server_shared_secret", RADIUS_SECRET)
            config.set("wpa", "1")
            config.set("wpa_key_mgmt", "WPA-EAP")
            config.set("wpa_pairwise", "TKIP")

        elif security == 'wpa2-eap':
            config.set("ieee8021x", "1")
            config.set("own_ip_addr", NAS_IP)
            config.set("auth_server_addr", RADIUS_IP)
            config.set("auth_server_port", RADIUS_PORT)
            config.set("auth_server_shared_secret", RADIUS_SECRET)
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
