#!/usr/bin/python
##
## Hostapd.py
##
## Author(s):
##  - Maxence VIALLON <mviallon@aldebaran-robotics.com>
##

#HOSTAP_DIR = "/usr/local/bin"
CONF_FILE = "/home/maxence/src/hostap/hostapd/hostapd.conf"
IFACE = "wlan1"
DRIVER = "nl80211"
MODE = "g"
CHANNEL = "1"

import subprocess
import os,signal
from time import sleep

class Config:
    """
    Class to write conf file
    """

    def __init__(self):
        self.config = open (CONF_FILE, "w")
        # Set default settings
        self.set("interface", IFACE)
        self.set("driver", DRIVER)
        self.set("hw_mode", MODE)
        self.set("channel", CHANNEL)

    def set(self, key, value):
        self.config.write("%s=%s\n" %(key,value))

    def push(self):
        self.config.close()

class Hostapd:
    """
    Class to manage hostapd
    """

    def __init__(self):
        self.cmd = ["hostapd", CONF_FILE]
        self.proc = subprocess.Popen(self.cmd)
        sleep(3)

    def open(self, ssid):

        config = Config()

        config.set("ssid", ssid)

        config.push()
        self.reload()

    def wpa2(self, ssid, passphrase):

        config = Config()

        config.set("ssid", ssid)
        self.ssid = ssid
        config.set("wpa", "2")
        config.set("wpa_passphrase", passphrase)
        self.passphrase = passphrase
        config.set("wpa_key_mgmt", "WPA-PSK")
        config.set("wpa_pairwise", "CCMP")

        config.push()
        self.reload()        

    def wpa(self, ssid, passphrase):

        config = Config()

        config.set("ssid", ssid)
        self.ssid = ssid
        config.set("wpa", "1")
        config.set("wpa_passphrase", passphrase)
        self.passphrase = passphrase
        config.set("wpa_key_mgmt", "WPA-PSK")
        config.set("wpa_pairwise", "TKIP")

        config.push()
        self.reload()        

    def reload(self):
        os.kill(self.proc.pid, signal.SIGHUP)
        sleep(1)

    def kill(self):
        os.kill(self.proc.pid, signal.SIGTERM)
        sleep(1)

if (__name__ == "__main__"):

    myhost = Hostapd()
    myhost.wpa2("stresstest","42424242")
