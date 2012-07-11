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

import subprocess
import os,signal
from time import sleep

class Config:
    """
    Class to write conf file
    """

    def __init__(self):
        self.config = open ("hostapd.conf", "w")
        self.set("interface", IFACE)

    def set(self, key, value):
        self.config.write("%s = %s\n" %(key,value))

    def push(self):
        self.config.close()

class Hostapd:
    """
    Class to manage hostapd
    """

    def __init__(self):
        self.cmd = ["hostapd", TEMP_FILE]
        self.proc = subprocess.Popen(self.cmd)
        sleep(3)

    def wpa2(self, ssid = "wpa2rezo", passphrase="12345678"):

        config = Config()

        config.set("ssid", ssid)
        config.set("wpa_passphrase", passphrase)

        config.push()

        self.reload()        

    def wpa(self, ssid = "wparezo", passphrase="12345678"):
        pass

    def reload(self):
        os.kill(self.proc.pid, signal.SIGHUP)
        sleep(1)

    def kill(self):
        os.kill(self.proc.pid, signal.SIGTERM)
        sleep(1)

if (__name__ == "__main__"):

    myhost = Hostapd()
    myhost.wpa2("wpatest","123")
