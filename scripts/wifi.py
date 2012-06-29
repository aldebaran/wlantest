#!/usr/bin/python
# coding: utf8
#
# Script de test wifi
#

WORK_DIR = "/home/maxence/src/wlantest"

import subprocess
import os
from time import sleep

def launch_hostap(conf):
    cmd = ["hostapd", WORK_DIR+"/hostap/"+conf, "-d"]
    proc = subprocess.Popen(cmd)
    sleep(3)

if (__name__ == "__main__"):
    # On liste les differentes conf hostap
    print ("Reading hostap directory ...")
    MODES = os.listdir(WORK_DIR+"/hostap/") 
    print MODES

    # Boucle principale
    for mode in MODES:
        launch_hostap(mode)
        print("Hostap running mode "+mode+"!")

