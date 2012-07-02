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
    print("Hostap running mode "+mode+"!")
    
    # On scan les réseaux
    print("Scanning wifi ...")
    cmd2 = ["/home/maxence/src/connman/test/test-connman", "scan", "wifi"]
    proc2 = subprocess.Popen(cmd2)
    proc2.wait()

    # On laisse à connman le temps de se connecter
    sleep(3)

    # TODO : Tester la connectivité

    # On tue hostap
    os.kill(proc.pid, signal.SIGTERM)
    sleep(1)

if (__name__ == "__main__"):
    # On liste les differentes conf hostap
    print ("Reading hostap directory ...")
    MODES = os.listdir(WORK_DIR+"/hostap/") 
    print MODES
    
    # TODO : Lancer le dhcp

    # Boucle principale
    for mode in MODES:
        mode_process(mode)

