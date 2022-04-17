import network
import esp
import gc
import time
import ubinascii
from config import conf
from led import statusLED


# Disable debugging
esp.osdebug(None)

sta_if = network.WLAN(network.STA_IF)


def setup():
    print('-' * 80)
    print('B O O T')
    print('-' * 80)

    if conf.data['network']['enabled'] is True:
        print('Connecting to network...')
        
        if not sta_if.isconnected():
            sta_if.active(True)

            sta_if.connect(
                conf.data['network']['ssid'],
                conf.data['network']['password']
            )
            sta_if.ifconfig('dhcp')
            while not sta_if.isconnected():
                time.sleep(1.0)

        if conf.data['network']['hostname']:
            print("Setting hostname to: " + conf.data['network']['hostname'])
            sta_if.config(dhcp_hostname=conf.data['network']['hostname'])

        if conf.data['general']['enable_webrepl'] is True:
            print('Starting WebREPL...')
            import webrepl
            webrepl.start()

    statusLED.blink(100, 1000)


def welcome():
    time.sleep(2)
    print('-' * 80)
    print('W E L C O M E')
    print('-' * 80)
    print('General:')
    print('Version:', conf.data['general']['config_version'])

    if conf.data['general']['enable_webrepl'] is True:
        print('WebREPL: Enabled')
    else:
        print('WebREPL: Disabled')

    if conf.data['general']['autosave_timeout'] > 0:
        print('Autosave: %ss' % (conf.data['general']['autosave_timeout'],))
    else:
        print('Autosave: Disabled')

    network_config = sta_if.ifconfig()
    print(' ')
    print('Network:')
    print('SSID:', sta_if.config('essid'))
    print('RSSI:', sta_if.status('rssi'))
    print('Hostname:', sta_if.config('dhcp_hostname'))
    print('IP:', network_config[0])
    print('Subnet:', network_config[1])
    print('Gateway:', network_config[2])
    print('DNS:', network_config[3])
    print('MAC:', ubinascii.hexlify(network.WLAN().config('mac'),':').decode())

    if conf.data['network']['enable_restapi'] is True:
        print('REST-API: Enabled')
        print('Host:', conf.data['network']['host'])
        print('Port:', conf.data['network']['port'])
    else:
        print('REST-API: Disabled')

    print(' ')
    print("Grinder:")
    print("Single Grind Duration: %s" % (conf.data['grinder']['single'],))
    print("Double Grind Duration: %s" % (conf.data['grinder']['double'],))
    print("Memorize last Grind: %s" % (conf.data['grinder']['memorize_timeout'],))

    print(" ")
    print('Stats:')
    print("Single Grinds done: %s" % (conf.data['stats']['single'],))
    print("Double Grinds done: %s" % (conf.data['stats']['double'],))
    print("Total grinding Time: %s" % (conf.data['stats']['duration'],))
    print('-' * 80)


setup()
welcome()
gc.collect()
