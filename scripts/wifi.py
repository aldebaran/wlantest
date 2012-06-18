#!/usr/bin/python
# coding: utf8
#
# Script de test wifi
#

WORK_DIR = "/home/maxence/src/wlantest"
MODES = ["wpa","wpa2"]

import subprocess
from time import sleep

def launch_hostap(conf):
    cmd = ["hostapd", WORK_DIR+"/hostap/"+conf+".conf", "-d"]
    proc = subprocess.Popen(cmd)
    sleep(3)

if (__name__ == "__main__"):
    print ("Initializing ...")

    for mode in MODES:
        launch_hostap(mode)
        print("Hostap running mode "+mode+"!")

