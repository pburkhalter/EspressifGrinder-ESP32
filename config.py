import asyncio
import binascii
import hashlib
import json
from machine import Pin
from lib.pathutils import exists, ensure_dir_exists

from lib.secret import generate_random_string, generate_bearer_token
from lib.singleton import singleton


# Pin mapping
pinSMO = Pin(33, Pin.IN, Pin.PULL_UP)   # Single Mode
pinDMO = Pin(32, Pin.IN, Pin.PULL_UP)   # Double Mode
pinGRN = Pin(25, Pin.OUT, Pin.PULL_UP)  # Grinder
pinLED = Pin(26, Pin.OUT, Pin.PULL_UP)  # LED
pinMSW = Pin(27, Pin.IN, Pin.PULL_UP)   # Microswitch


WIFI_PATH = './secrets/wifi.json'
TOKENS_PATH = './secrets/tokens.json'
SECRETS_PATH = './secrets/secret.json'
CONFIG_PATH = 'configs/configs.json'
CONFIG_DEFAULT_PATH = 'configs/config.default.json'


def load_json_from_file(filepath):
    try:
        f = open(filepath, 'r')
        data = json.loads(f.read())
        f.close()
        return data

    except (OSError, KeyError, ValueError):
        print('Could not read from file: ' + filepath)
        return {}


def write_json_to_file(filepath, data):
    try:
        directory, _ = filepath.rsplit('/', 1)
        ensure_dir_exists(directory)

        with open(filepath, 'w') as f:
            json.dump(data, f)

        return True
    except OSError as e:
        print(f"Could not write to file: {filepath}. Error: {e}")
        return False


@singleton
class Config(object):

    def __init__(self):
        self.data = {}

        self.__runtime_defaults = {
            'modeset': 'grind',
        }

        if not exists(CONFIG_PATH) or not load_json_from_file(CONFIG_PATH):
            print("No configs file found. Creating from default config file...")
            write_json_to_file(CONFIG_PATH, load_json_from_file(CONFIG_DEFAULT_PATH))

        if exists(CONFIG_PATH):
            object.__setattr__(self, 'data', load_json_from_file(CONFIG_PATH))

        if exists(WIFI_PATH):
            self.data['wifi'] = load_json_from_file(WIFI_PATH)

        self.data.update(self.__runtime_defaults)

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def load(self, json_string):
        try:
            new_data = json.loads(json_string)

            # Load default configuration to ensure all keys are present
            default_config = load_json_from_file(CONFIG_DEFAULT_PATH)

            # Check if every key in default config is present in new_data
            missing_keys = [key for key in default_config if key not in new_data]
            if missing_keys:
                print(f"Missing keys in provided configuration: {missing_keys}")
                return False

            self.data = new_data
            self.save()
        except:
            return False

        return True

    def save(self):
        data = self.data.copy()

        wifi = data.pop('wifi', None)

        for key in self.__runtime_defaults:
            data.pop(key, None)

        write_json_to_file(CONFIG_PATH, data)
        if wifi is not None:
            write_json_to_file(WIFI_PATH, wifi)


@singleton
class TokenStore(object):
    def __init__(self):
        self.secret = None
        self.data = {}

        self.__runtime_defaults = {
            'register_timeout': 300,
            'enable_register': False,
        }

        if exists(SECRETS_PATH):
            self.secret = load_json_from_file(SECRETS_PATH)['token_secret']
        else:
            self.secret = generate_random_string()
            write_json_to_file(SECRETS_PATH, {'token_secret': self.secret})

        if exists(TOKENS_PATH):
            self.data = load_json_from_file(TOKENS_PATH)

        self.data.update(self.__runtime_defaults)

    def enable_register(self, timeout=None):
        timeout = timeout or self.data['register_timeout']

        async def _delayed(to):
            await asyncio.sleep(to)
            self.disable_register()

        asyncio.create_task(_delayed(timeout))
        self.data['enable_register'] = True

    def disable_register(self):
        self.data['enable_register'] = False

    def create_token(self, client_id):
        token = generate_bearer_token(self.secret)
        self.data[client_id] = token
        self.save()

        return token

    def invalidate_token(self, client_id):
        if client_id not in self.data:
            return False

        del self.data[client_id]
        return True

    def validate_token(self, token):
        for client_id in self.data:
            if self.data[client_id] == token:
                return True
        return False

    def save(self):
        data = self.data.copy()

        for key in self.__runtime_defaults:
            data.pop(key, None)

        write_json_to_file(TOKENS_PATH, data)


conf = Config()
tokens = TokenStore()
