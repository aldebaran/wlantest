Wlantest
========

Wlantest is an automatic wireless testing script written in Python which aims at checking 
ConnMan behaviour. (http://connman.net)

For every test, Wlantest runs hostapd on an interface according to a config file and tries
to connect to it using ConnMan. The result is output in /var/log/wlantest.log.


Misc notes
----------

* Wlantest must be launched at root

* There are a few parameters in /etc/wlantest/main.conf which have to be set before
running Wlantest.

* ConnMan should be launched with -I <iface> where iface is the interface which will run
the AP.

* If a dhcpd is running, do not forget to set up an ip address to the AP interface so
that the dhcpd can listen on it.


Testing environment
-------------------

The minimum testing requirement is a machine with two wlan interfaces:
- An interface used in AP mode on which hostapd is running
- An interface used in STA mode that connman operates

Extra setup may be composed of:
- A radius server to test WPA-EAP
- A dhcpd to speed up connman connection process

Here is an example of our test environment:

             ----------------------
            |     Test Machine     |
            |        --------------|
            |       |mac80211_hwsim|
            |       |              |
            |       |       wlan0--|        ---------------
            |       |        (STA) |       | Radius Server |
            |       |              |       |               |
            |       |       wlan1--|       |               |
            | eth0  |        (AP)  |       |     eth0      |
             ---|------------------         -------|-------
                |__________________________________|

The script used to setup the above test environnment is supplied FYI in launcher/wlantest.sh


Wlantest configuration test file format
---------------------------------------

Wlantest uses configuration files to load tests. Wlantest will be looking
for its configuration files in /etc/wlantest/cfg/. They must have a .cfg suffix.

Allowed fields
++++++++++++++

A value can either be a single item or coma-separated items.

[Description]
- description : A short description of the test.

[AP]
- ssid : A string representation of an 802.11 SSID. If this field is not present,
wlantest will use id_test as ssid.
- hidden : Must be set to true if the AP is hidden, otherwise it can be ommited.
- security : Security type, must be in {open, wpa-psk, wpa2-psk, wpa-eap, wpa2-eap}
- mode : Radio mode, must be in {a, b, g, n, gn}
- channel : Channel frequency, must be choosen accordingly to mode.
- channelposition : Channel position, must be upper or lower. It is mandatory for 40Mhz
bandwith. If not set, 20Mhz bandwith operation.
- method : EAP method, which is mandatory for wpa-eap or wpa2-eap security. It must be
in {PEAP, TTLS}
- phase2 : phase2 type for EAP tunneld methods, must be in {MSCHAPV2, MD5}
- identity : The identity used in EAP authentification.
- passphrase : Either quoted string if passphrase or unquoted hexadecimal if raw key
                If wep key (5 or 13 characters passphrase, or 10 or 26 digits key),
                    or wpa key (8 to 63 characters passphrase or 64 digits key),
                    or EAP password unquoted string.
Examples : "vwxyz" (wep passphrase) or 123456789a (wep key) or "12345678" (wpa passphrase)

[Connection]
- mode : The mode of connection, must be in {manual, auto}
- identity : The identity used to connect to EAP network.
- passphrase : Either wep key, wpa psk or eap password used by the agent to connect.

[Result]
- state : Expected connman state after connect attempt. Must be in {idle, ready, online}
- error : Expected connman connect error. If no error expected, must be set to None.

