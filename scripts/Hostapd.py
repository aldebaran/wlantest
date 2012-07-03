#!/usr/bin/python
##
## Hostapd.py
##
## Author(s):
##  - Maxence VIALLON <mviallon@aldebaran-robotics.com>
##

#HOSTAP_DIR = "/usr/local/bin"
#CONF_DIR = "/usr/share/wlantest/hostap"
CONF_DIR = "/home/maxence/src/wlantest/hostap"
#TEMP_FILE = "/home/nao/hostapd.conf"
TEMP_FILE = "/home/maxence/src/hostap/hostapd/hostapd.conf"

import subprocess
import shutil
import os,signal
from time import sleep

class Hostapd:
    """
    Class to configure hostapd
    """

    def __init__(self):
        self.cmd = ["hostapd", TEMP_FILE]
        self.proc = subprocess.Popen(self.cmd)
        sleep(3)

    def reload(self, conf):
        # Copying new conf
        shutil.copy(CONF_DIR+"/"+conf, TEMP_FILE)

        # Reloading hostap
        os.kill(self.proc.pid, signal.SIGHUP)
        sleep(1)
    
    def kill(self):
        os.kill(self.proc.pid, signal.SIGTERM)
        sleep(1)
