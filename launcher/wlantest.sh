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
ip link set dev eth0 up
ip a add dev eth0 "${IP_LOCAL}"
ip link set dev wlan1 up
ip a add dev wlan1 "${IP_AP}"
ip link set dev wlan0 up

#Starting dhcpd
#dhcpd -cf /etc/wlantest/dhcpd.conf

#Starting Wlantest
wlantest
