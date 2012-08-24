#!/bin/sh
##
## Script for setting up OpenNao for wlantest
##
## Author(s):
##  - Maxence VIALLON <mviallon@aldebaran-robotics.com>
##

IP_LOCAL=192.168.2.4
IP_AP=192.168.3.1

#Loading virtual interfaces
modprobe mac80211_hwsim

#Setting up regulatory domain
iw reg set FR

#Setting up ip parameters
ifconfig eth0 "${IP_LOCAL}"
ifconfig wlan1 "${IP_AP}"

#Starting dhcpd
dhcpd -cf /etc/wlantest/dhcpd.conf

#Starting Wlantest
wlantest
