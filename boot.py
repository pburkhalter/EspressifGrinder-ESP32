import gc
import esp
import time
import ntptime

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
        netman.create_ap(
            ssid=conf['network']['default_ssid'],
            password=conf['network']['default_password']
        )

        if MicroDNSSrv.Create({"coffeegrinder.dev": "192.168.4.1",
                               "*" :                "192.168.0.254"}):
            print("MicroDNSSrv started.")
        else:
            print("Error starting MicroDNSSrv...")

    elif conf['network']['enable']:
        print('Connecting to network...')
        netman.connect(
            conf.data['wifi']['ssid'],
            conf.data['wifi']['password']
        )
        netman.set_powerstate('off')

        print('Setting hostname to ' + conf.data['network']['hostname'])
        netman.hostname = conf.data['network']['hostname']
        netman.use_dhcp()

        print('Waiting for Wifi to become ready...')
        if not netman.wait_until_wifi_ready(timeout=30):
            netman.create_ap(
                ssid=conf['network']['default_ssid'],
                password=conf['network']['default_ssid']
            )

        print('Syncing time with NTP...')
        try:
            ntptime.settime()
            now = time.localtime()
            print("Time: {}.{}.{} {}:{}:{}".format(now[2], now[1], now[0], now[3], now[4], now[5]))
        except:
            print("Error syncing time")

        LED(pinLED).blink(200, 1000)


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
    print('')
    print('Device:')
    print('- Machine:\t', device.machine)
    print('- Model:\t', device.model)
    print('- Version:\t', 'Micropython ', device.version)
    print('- Node:\t\t', device.node)
    print('- CPU:\t\t', device.cpu_freq / 1000 / 1000, 'Mhz')
    print('- Memory:\t', device.mem_total / 1024, 'kB')
    print('')

    if netman.isconnected:
        print('Network:')
        print('- SSID:\t\t',netman.ssid)
        print('- RSSI:\t\t', netman.rssi)
        print('- Hostname:\t', netman.hostname)
        print('- IP Address:\t', netman.ipaddr)
        print('- Netmask:\t', netman.netmask)
        print('- Gateway:\t', netman.gateway)
        print('- DNS:\t\t', netman.dns)
        print('- MAC:\t\t', netman.mac)

        if conf['api']['enable']:
            print('- REST-API:\t Enabled')
            print('- Host:\t\t', conf['api']['host'])
            print('- Port:\t\t', conf['api']['port'])
        else:
            print('- REST-API:\t Disabled')

    if conf['general']['initialized']:
        print('')
        print("Grinder:")
        print("- Single Grind Duration: %s" % (conf['grinder']['duration']['single'],))
        print("- Double Grind Duration: %s" % (conf['grinder']['duration']['double'],))
        print("- Memorize last Grind for: %s" % (conf['grinder']['duration']['memorize'],))


setup()
welcome()
gc.collect()
