import network
import ubinascii


iface = network.WLAN(network.STA_IF)


class NetworkManager:

    def __init__(self):
        iface.active(True)

    @staticmethod
    def connect(ssid, password):
        iface.connect(ssid, password)

    @staticmethod
    def use_dhcp():
        iface.ifconfig('dhcp')

    @property
    def powerstate(self):
        return iface.config('pm')

    def set_powerstate(self, mode):
        if mode == 'performance':
            iface.config(pm=iface.PM_PERFORMANCE)
        elif mode == 'off':
            iface.config(pm=iface.PM_NONE)
        elif mode == 'powersave':
            iface.config(pm=iface.PM_POWERSAVE)  # disable power management

    @property
    def isconnected(self):
        return iface.isconnected()

    @property
    def ssid(self):
        return iface.config('ssid')

    @property
    def rssi(self):
        return ' '.join([str(iface.status('rssi')), 'dB'])

    @property
    def hostname(self):
        return network.hostname()

    @hostname.setter
    def hostname(self, hostname):
        network.hostname(hostname)

    @property
    def ipaddr(self):
        return iface.ifconfig()[0]

    @property
    def netmask(self):
        return iface.ifconfig()[1]

    @property
    def gateway(self):
        return iface.ifconfig()[2]

    @property
    def dns(self):
        return iface.ifconfig()[3]

    @property
    def mac(self):
        return ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
