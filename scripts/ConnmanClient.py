#!/usr/bin/python
##
## ConnmanClient.py
##
## Author(s):
##  - Maxence VIALLON <mviallon@aldebaran-robotics.com>
##

import dbus
import threading

class AgentThread (threading.Thread):

    def __init__(self, daemon):
        threading.Thread.__init__(self)
        self.daemon = daemon


    def run(self):
        # TODO : Agent main loop
        pass

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

        self.agent = AgentThread(True)

        self.agent.start()

    def scan(self):
        self.technology.Scan()

    def serviceisConnected(self, ServiceId):
        for path,properties in self.manager.GetServices(): 
            if path == "/net/connman/service/" + ServiceId:
                    if properties["State"] in ("ready","online"):
                        return True
                    else:
                        return False

    def getServiceId(self, ServiceName):
        for path,properties in self.manager.GetServices(): 
            if properties.get("Name", "") == ServiceName:
                ServiceId = path[path.rfind("/") + 1:]
                return ServiceId

if (__name__ == "__main__"):
    myConn = ConnmanClient()
    ServiceId = myConn.getServiceId("FreeWifi")
    print ServiceId
    if myConn.serviceisConnected(ServiceId):
        print "Success"
    else:
        print "Fail"
