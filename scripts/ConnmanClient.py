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

    def serviceisConnected(self, serviceId=None):
        for path,properties in self.manager.GetServices(): 
            if properties["Type"] == "wifi":
                if properties["State"] in ("ready","online"):
                    print "Success !"
                else:
                    print "Fail"

    def getServiceId(self, serviceName, security):
        pass

if (__name__ == "__main__"):
    myConn = ConnmanClient()
    myConn.serviceisConnected()
