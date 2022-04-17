from machine import Pin
import json
import os
import uasyncio


# Version
VERSION = "0.0.1"
CONFIG_VERSION = "0.0.1"


# Pin mapping
pinSMO = Pin(33, Pin.IN, Pin.PULL_UP)   # Single Mode
pinDMO = Pin(32, Pin.IN, Pin.PULL_UP)   # Double Mode
pinGRN = Pin(25, Pin.OUT, Pin.PULL_UP)    # Grinder
pinLED = Pin(26, Pin.OUT, Pin.PULL_UP)    # LED
pinMSW = Pin(27, Pin.IN, Pin.PULL_UP)   # Microswitch


async def autosave(timeout):
    while True:
        await uasyncio.sleep(timeout)
        conf.write()


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class Config(object):

    def __init__(self):
        self.data = {}
        self.defaults = {}

        self.defaults['general'] = {}
        self.defaults['general']['config_version'] = CONFIG_VERSION
        self.defaults['general']['enable_webrepl'] = True
        self.defaults['general']['autosave_timeout'] = 600  # in seconds

        self.defaults['network'] = {}
        self.defaults['network']['enabled'] = False
        self.defaults['network']['ssid'] = ''
        self.defaults['network']['password'] = ''
        self.defaults['network']['hostname'] = 'coffegrinder'

        self.defaults['network']['enable_restapi'] = False
        self.defaults['network']['host'] = '0.0.0.0'
        self.defaults['network']['port'] = 80
        
        self.defaults['grinder'] = {}
        self.defaults['grinder']['single'] = 4000
        self.defaults['grinder']['double'] = 8000
        self.defaults['grinder']['memorize_timeout'] = 5000
        
        self.defaults['stats'] = {}
        self.defaults['stats']['duration'] = 0
        self.defaults['stats']['single'] = 0
        self.defaults['stats']['double'] = 0

        if not self.read():
            print("No config file found. Creating...")
            self.write(self.defaults)

    def read(self, apply=True):
        try:
            print("Reading config from file...")
            f = open('config.json', 'r')
            data = json.loads(f.read())
            f.close()

            if not self.defaults['general']['config_version'] == data['general']['config_version']:
                print('Config file versions do not match!')
                print('Backing up old config and creating a new one...')
                os.rename('config.json', 'config.json.old')
                self.write(self.defaults)

            if apply:
                self.data = data
                
        except OSError:
            print("Could not read config file! Setting default values...")
            self.data = self.defaults
            print('Creating a new config file with default values...')
            self.write(compare=False)
            return self.defaults

        except (KeyError, ValueError):
            print('Key or Value not found. Config-file seems corrupted!')
            print('Backing up old config and creating a new one...')
            os.rename('config.json', 'config.json.old')
            return self.write(self.defaults)

        return data

    def write(self, data=None, compare=True):
        data = data or self.data

        if compare is True:
            if self.read() == data:
                print("Config did not change, skipping...")
                return self.data
        try:
            print("Writing config to file...")
            f = open('config.json', 'w')
            f.write(json.dumps(data))
            f.close()
            print('Saved config...')
        except OSError:
            print('Could not write config to file!')

        self.data = data
        return self.data

    def reset_stats(self):
        print('Resetting statistics...')
        self.data['stats'] = self.defaults['stats']


conf = Config()
