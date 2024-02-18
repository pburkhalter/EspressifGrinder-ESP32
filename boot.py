import esp
import gc
import time
import network

from config import conf, pinLED

from lib.led import LED
from lib.device import DeviceInfo
from lib.net import NetworkManager


# Disable debugging
esp.osdebug(None)

device = DeviceInfo()
netman = NetworkManager()


def setup():
    if not conf['general']['initialized']:
        from lib.microdnssrv import MicroDNSSrv

        print('Machine not initialized. Creating access point "CoffeGrinder"...')
        ap = network.WLAN(network.AP_IF)
        ap.active(True)

        ap.config(
            essid='CoffeeGrinder',
            password='C0ff3Gr1nd3r',
            channel=6,
            authmode=network.AUTH_WPA2_PSK
        )

        network.hostname('coffeegrinder')

        if MicroDNSSrv.Create({"coffeegrinder.dev": "192.168.4.1",
                               "*" :                "192.168.0.254"}):
            print("MicroDNSSrv started.")
        else:
            print("Error to starts MicroDNSSrv...")

    elif conf['network']['enable']:
        print('Connecting to network...')

        netman.set_powerstate('off')
        netman.connect(
            conf.data['wifi']['ssid'],
            conf.data['wifi']['password']
        )

        netman.hostname = conf.data['network']['hostname']
        netman.use_dhcp()

        while not netman.isconnected:
            time.sleep(1.0)

        led_controller = LED(pinLED)
        led_controller.blink(200, 1000)


def welcome():
    print('-' * 80)
    print('W E L C O M E')
    print('-' * 80)
    print('')
    print('About:')
    print('- Version:\t', conf['general']['version'])
    print('- Manufacturer:\t', conf['machine']['manufacturer'])
    print('- Model:\t', conf['machine']['model'])
    print('- Serial:\t', conf['machine']['serial'])
    print('Device:')
    print('- Machine:\t', device.machine)
    print('- Model:\t', device.model)
    print('- Version:\t', device.version)
    print('- Node:\t\t', device.node)
    print('- CPU Hz:\t', device.cpu_freq)
    print('- Memory:\t', device.mem_total)
    print('')

    if netman.isconnected:
        print('Network:')
        print('- SSID:\t',netman.ssid)
        print('- RSSI:\t', netman.rssi)
        print('- Hostname:\t', netman.hostname)
        print('- IP Address:\t', netman.ipaddr)
        print('- Netmask:\t', netman.netmask)
        print('- Gateway:\t', netman.gateway)
        print('- DNS:\t', netman.dns)
        print('- MAC:\t', netman.mac)

        if conf['api']['enable']:
            print('- REST-API:\t Enabled')
            print('- Host:\t', conf['api']['host'])
            print('- Port:\t', conf['api']['port'])
        else:
            print('- REST-API:\t Disabled')

    if conf['general']['initialized']:
        print('')
        print("Grinder:")
        print("- Single Grind Duration: %s" % (conf['grinder']['duration_single'],))
        print("- Double Grind Duration: %s" % (conf['grinder']['duration_double'],))
        print("- Memorize last Grind for: %s" % (conf['grinder']['memorize_timeout'],))


setup()
welcome()
gc.collect()
