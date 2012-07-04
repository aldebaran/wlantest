#!/usr/bin/python
##
## ConnmanClient.py
##
## Author(s):
##  - Maxence VIALLON <mviallon@aldebaran-robotics.com>
##

import dbus

class ConnmanClient:
    """
    Class to get information from ConnMan
    """

    def __init__(self):
        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(self.bus.get_object("net.connman", "/"), \
                "net.connman.Manager")
        self.technology = dbus.Interface(self.bus.get_object("net.connman", \
                "/net/connman/technology/wifi"), "net.connman.Technology")

    def scan(self):
        self.technology.Scan()

    def serviceisConnected(self, Name):
        for path,properties in self.manager.GetServices(): 
            if "Name" in properties.keys():
                if properties["Name"] == Name:
                    if properties["State"] in ("ready","online"):
                        print "Successfuly connected to "+Name
                    else:
                        print "[!] Failed to connect to "+Name

    def getServiceId(self, serviceName, security):
        pass

if (__name__ == "__main__"):
    myConn = ConnmanClient()
    myConn.serviceisConnected("FreeWifi")
