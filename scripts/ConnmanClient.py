#!/usr/bin/python
##
## ConnmanClient.py
## Login : <maxence@mviallon-de>
## Started on  Tue Jul  3 10:39:14 2012 maxence
## $Id$
##
## Author(s):
##  - maxence <>

import dbus

class ConnmanClient:
    """
    Class to get information from ConnMan
    """
    bus = None
    manager = None
    technology = None

    def __init__(self):
        bus = dbus.Systembus()
        manager = dbus.Interface(bus.get_object("net.connman", "/"),"net.connman.Manager")
        technology = dbus.Interface(bus.get_object("net.connman", \
                "/net/connman/technology/wifi"), "net.connman.Technology")

    def scan(self):
        technology.Scan()

    def serviceisConnected(self, serviceId):
        pass
    def getServiceId(self, serviceName, security)
        pass
