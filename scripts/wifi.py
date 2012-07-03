#!/usr/bin/python
# coding: utf8
#
# Script de test wifi
#

WORK_DIR = "/home/maxence/src/wlantest"

import os
from time import sleep

from ConnmanClient import ConnmanClient
from Hostapd import Hostapd

def mode_process(conf):
    # On lance hostap
    hostapd.reload(conf)
    print("Hostap running mode "+mode+"!")
    
    # On scan les réseaux
    print("Scanning wifi ...")
    connman.scan()
    
    # On laisse à connman le temps de se connecter
    sleep(5)
    
    # On teste la connectivité
    connman.serviceisConnected()
    
if (__name__ == "__main__"):
    
    # On liste les differentes conf hostap
    print ("Reading hostap directory ...")
    MODES = os.listdir(WORK_DIR+"/hostap/") 
    print MODES
    
    # TODO : Lancer le dhcp
    
    # Création des objets
    connman = ConnmanClient()
    hostapd = Hostapd()
    
    # Boucle principale
    for mode in MODES:
        mode_process(mode)

    # Killing Hostapd
    hostapd.kill()

