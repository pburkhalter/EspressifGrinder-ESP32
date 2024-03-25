import time
import network
import ubinascii


class NetworkManager:

    def __init__(self):
        self.iface = None
        self.setmode()

    def setmode(self, mode='client'):
        if mode == 'ap':
            self.iface = network.WLAN(network.AP_IF)
        if mode == 'client':
            self.iface = network.WLAN(network.STA_IF)

    def connect(self, ssid, password):
        self.iface = network.WLAN(network.STA_IF)
        self.iface.active(True)
        print("Connecting to network '{}'...".format(ssid))
        self.iface.connect(ssid, password)

    def create_ap(self, ssid, password, channel=6, authmode=network.AUTH_WPA2_PSK):
        self.iface = network.WLAN(network.AP_IF)
        self.iface.active(True)

        self.iface.config(
            essid=ssid,
            password=password,
            channel=channel,
            authmode=authmode
        )

    def use_dhcp(self):
        self.iface.ifconfig('dhcp')

    def wait_until_wifi_ready(self, timeout=30):
        start_time = time.time()

        while not self.isconnected:
            if time.time() - start_time > timeout:
                print("Connection timeout")
                return False

            status = self.iface.status()

            # Handle specific statuses with messages but do not return
            if status == network.STAT_NO_AP_FOUND:
                print("No AP found, retrying...")
            elif status == network.STAT_WRONG_PASSWORD:
                print("Wrong password for AP specified!")
                return False

            time.sleep(1.0)  # Wait a bit before trying again

        # Successfully connected
        return True

    @property
    def powerstate(self):
        return network.config('pm')

    def set_powerstate(self, mode):
        if mode == 'performance':
            self.iface.config(pm=network.WLAN.PM_PERFORMANCE)
        elif mode == 'off':
            self.iface.config(pm=network.WLAN.PM_NONE)
        elif mode == 'powersave':
            self.iface.config(pm=network.WLAN.PM_POWERSAVE)

    @property
    def isconnected(self):
        return self.iface.isconnected()

    @property
    def ssid(self):
        return self.iface.config('ssid')

    @property
    def rssi(self):
        return ' '.join([str(self.iface.status('rssi')), 'dB'])

    @property
    def hostname(self):
        return network.hostname()

    @hostname.setter
    def hostname(self, hostname):
        network.hostname(hostname)

    @property
    def ipaddr(self):
        return self.iface.ifconfig()[0]

    @property
    def netmask(self):
        return self.iface.ifconfig()[1]

    @property
    def gateway(self):
        return self.iface.ifconfig()[2]

    @property
    def dns(self):
        return self.iface.ifconfig()[3]

    @property
    def mac(self):
        return ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()

