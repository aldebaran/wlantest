#!/usr/bin/python
##
## ConnmanClient.py
##
## Author(s):
##  - Maxence VIALLON <mviallon@aldebaran-robotics.com>
##

CONF = "/var/lib/connman/connman.config"
TIMEOUT = 90

import ConfigParser

import dbus

import dbus.service
import dbus.mainloop.glib
import gobject

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
        loop.quit()

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
                    in_signature='oa{sv}', out_signature='a{sv}')
    def RequestInput(self, path, fields):
        response = {}

        if fields.has_key("Name"):
            response.update(self.input_hidden())
        if fields.has_key("Passphrase"):
            response.update(self.input_passphrase())
        if fields.has_key("Username"):
            response.update(self.input_username())

        print response
        return response

    @dbus.service.method("net.connman.Agent",
                    in_signature='', out_signature='')
    def Cancel(self):
        pass

def property_changed(name, value):
    """
    Signal handler for property chaned
    """
    if name == "State":
        val = str(value)
        if val in ('ready', 'online'):
            loop.quit()
            print "Autoconnect callback"

class ConnmanClient:
    """
    Class to get information from ConnMan
    """

    def __init__(self):

        # Setting up bus
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(self.bus.get_object("net.connman", "/"), \
                "net.connman.Manager")
        self.technology = dbus.Interface(self.bus.get_object("net.connman", \
                "/net/connman/technology/wifi"), "net.connman.Technology")

        agentpath = "/test/agent"
        self.agent = Agent(self.bus, agentpath)
        self.manager.RegisterAgent(agentpath)

        self.error = None

    def handle_connect_error(self, error):
        loop.quit()
        self.error = error
        print "Connect returns an error"

    def handle_connect_reply(self):
        loop.quit()
        self.error = None
        print "Connect callback"

    def autoconnect_timeout(self):
        loop.quit()
        print "Autoconnect timeout"

    def scan(self):
        self.technology.Scan()

    def connect(self, ServiceId, **credentials):
        path = "/net/connman/service/" + ServiceId

        service = dbus.Interface(self.bus.get_object("net.connman", path),
                            "net.connman.Service")

        if credentials.has_key("name"):
            self.agent.name = credentials["name"]
        if credentials.has_key("passphrase"):
            self.agent.passphrase = credentials["passphrase"]
        if credentials.has_key("identity"):
            self.agent.identity = credentials["identity"]

        service.Connect(timeout=60000,
                        reply_handler=self.handle_connect_reply,
                        error_handler=self.handle_connect_error)

        global loop
        loop = gobject.MainLoop()
        loop.run()

    def autoconnect(self):
        timeout = gobject.timeout_add(1000*TIMEOUT, self.autoconnect_timeout)

        signal = self.bus.add_signal_receiver(property_changed,
            bus_name="net.connman",
            dbus_interface="net.connman.Service",
            signal_name="PropertyChanged")

        global loop
        loop = gobject.MainLoop()
        loop.run()

        gobject.source_remove(timeout)
        signal.remove()

    def disconnect(self, ServiceId):

        path = "/net/connman/service/" + ServiceId

        service = dbus.Interface(self.bus.get_object("net.connman", path),
                            "net.connman.Service")

        try:
            service.Disconnect(timeout=60000)
        except dbus.DBusException, error:
            print "%s: %s" % (error._dbus_error_name, error.message)

    def remove(self, ServiceId):

        path = "/net/connman/service/" + ServiceId

        service = dbus.Interface(self.bus.get_object("net.connman", path),
                            "net.connman.Service")

        try:
            service.Remove()
        except dbus.DBusException, error:
            print "%s: %s" % (error._dbus_error_name, error.message)

    def getState(self, ServiceId):
        for path,properties in self.manager.GetServices(): 
            if path == "/net/connman/service/" + ServiceId:
                    return properties["State"]

    def getServiceId(self, ServiceName):
        for path,properties in self.manager.GetServices(): 
            if properties.get("Name", "hidden") == ServiceName:
                ServiceId = path[path.rfind("/") + 1:]
                return ServiceId
        raise IOError('Service not found !')

    def getConnectError(self):
        error = self.error
        self.error = None
        return error

    def setConfig(self, **param):
        config = ConfigParser.RawConfigParser()
        config.optionxform = str
        config.read(CONF)
        
        section = "service_"+param['Name']
        config.remove_section(section)
        config.add_section(section)
        config.set(section, "Type", "wifi")
        for item in param:
            if param.has_key(item):
                config.set(section, item, param[item])

        with open(CONF, 'w') as configfile:
            config.write(configfile)

    def clearConfig(self, name):
        config = ConfigParser.RawConfigParser()
        config.read(CONF)

        section = "service_"+name
        config.remove_section(section)

        with open(CONF, 'w') as configfile:
            config.write(configfile)

if (__name__ == "__main__"):
    myConn = ConnmanClient()
    myConn.autoconnect()
