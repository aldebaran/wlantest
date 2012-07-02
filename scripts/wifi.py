#!/usr/bin/python
# coding: utf8
#
# Script de test wifi
#

WORK_DIR = "/home/maxence/src/wlantest"

import subprocess
import os,signal
from time import sleep

def mode_process(conf):
    # On lance hostap
    cmd = ["hostapd", WORK_DIR+"/hostap/"+conf, "-d"]
    proc = subprocess.Popen(cmd)
    sleep(3)
    
    # On scan les réseaux, connman se connecte automatiquement
    cmd2 = ["connman", "scan", "wifi"]
    proc2 = subprocess.Popen(cmd2)
    sleep(3)

    # On tue hostap
    os.kill(proc.pid, signal.SIGTERM)
    sleep(3)

if (__name__ == "__main__"):
    # On liste les differentes conf hostap
    print ("Reading hostap directory ...")
    MODES = os.listdir(WORK_DIR+"/hostap/") 
    print MODES
    
    # TODO : Lancer le dhcp

    # Boucle principale
    for mode in MODES:
        mode_process(mode)
        print("Hostap running mode "+mode+"!")

