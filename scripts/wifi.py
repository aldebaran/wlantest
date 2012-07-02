#!/usr/bin/python
# coding: utf8
#
# Script de test wifi
#

WORK_DIR = "/home/maxence/src/wlantest"
IP_AP = "192.168.3.1"

import subprocess
import os,signal
from time import sleep

def scan_wifi():
    cmd = ["/home/maxence/src/connman/test/test-connman", "scan", "wifi"]
    proc = subprocess.Popen(cmd)
    proc.wait()

def ping_ap():
    cmd = ["ping", "-c", "1", IP_AP]
    proc = subprocess.Popen(cmd)
    proc.wait()
    return proc.returncode

def mode_process(conf):
    # On lance hostap
    cmd = ["hostapd", WORK_DIR+"/hostap/"+conf, "-d"]
    proc = subprocess.Popen(cmd)
    sleep(3)
    print("Hostap running mode "+mode+"!")
    
    # On scan les réseaux
    print("Scanning wifi ...")
    scan_wifi()

    # On laisse à connman le temps de se connecter
    sleep(3)

    # On teste la connectivité
    if not ping_ap():
        print ("Sucess !")
    else:
        print ("Failure !")

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

