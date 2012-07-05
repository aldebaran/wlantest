#!/usr/bin/python
##
## ConnmanClient.py
##
## Author(s):
##  - Maxence VIALLON <mviallon@aldebaran-robotics.com>
##

import gobject

import dbus
import dbus.service
import dbus.mainloop.glib
import threading

class Agent(dbus.service.Object):
	name = None
	ssid = None
	identity = None
	passphrase = None
	wpspin = None
	username = None
	password = None

	@dbus.service.method("net.connman.Agent",
					in_signature='', out_signature='')
	def Release(self):
		mainloop.quit()

	def input_passphrase(self):
		response = {}

		if self.identity:
			response["Identity"] = self.identity
		if self.passphrase:
			response["Passphrase"] = self.passphrase
		if self.wpspin:
			response["WPS"] = self.wpspin

		return response

	def input_username(self):
		response = {}

		if self.username:
			response["Username"] = self.username
		if self.password:
			response["Password"] = self.password

		return response

	def input_hidden(self):
		response = {}

		if self.name:
			response["Name"] = self.name
		if self.ssid:
			response["SSID"] = self.ssid

		return response

	@dbus.service.method("net.connman.Agent",
					in_signature='oa{sv}',
					out_signature='a{sv}')
	def RequestInput(self, path, fields):
		response = {}

		if fields.has_key("Name"):
			response.update(self.input_hidden())
		if fields.has_key("Passphrase"):
			response.update(self.input_passphrase())
		if fields.has_key("Username"):
			response.update(self.input_username())

		return response
    
	@dbus.service.method("net.connman.Agent",
					in_signature='', out_signature='')
	def Cancel(self):
		pass

class AgentThread (threading.Thread):

    def __init__(self, daemon):
        threading.Thread.__init__(self)
        self.daemon = daemon
        
        gobject.threads_init()
        dbus.mainloop.glib.threads_init()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    def run(self):
        mainloop = gobject.MainLoop()
        mainloop.run()

class ConnmanClient:
    """
    Class to get information from ConnMan
    """

    def __init__(self):

        self.agent = AgentThread(True)

        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(self.bus.get_object("net.connman", "/"), \
                "net.connman.Manager")
        self.technology = dbus.Interface(self.bus.get_object("net.connman", \
                "/net/connman/technology/wifi"), "net.connman.Technology")

        # Initializing Agent
        path = "/test/agent"
        self.object = Agent(self.bus,path)
        self.manager.RegisterAgent(path)
        self.agent.start()

    def scan(self):
        self.technology.Scan()

    def connect(self, ServiceId):
        
        path = "/net/connman/service/" + ServiceId

        service = dbus.Interface(self.bus.get_object("net.connman", path),
		    				"net.connman.Service")

        try:
            service.Connect(timeout=60000)
        except dbus.DBusException, error:
            print "%s: %s" % (error._dbus_error_name, error.message)

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

    def setPassphrase(self, Passphrase):
        self.object.passphrase = Passphrase

if (__name__ == "__main__"):
    myConn = ConnmanClient()
    ServiceId = myConn.getServiceId("FreeWifi")
    print ServiceId
    if myConn.serviceisConnected(ServiceId):
        print "Success"
    else:
        print "Fail"
