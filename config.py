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

        if not exists(CONFIG_PATH) or not load_json_from_file(CONFIG_PATH):
            print("No configs file found. Creating from default configs file...")
            write_json_to_file(CONFIG_PATH, load_json_from_file(CONFIG_DEFAULT_PATH))

        if exists(CONFIG_PATH):
            object.__setattr__(self, 'data', load_json_from_file(CONFIG_PATH))

        if exists(WIFI_PATH):
            self.data['wifi'] = load_json_from_file(WIFI_PATH)

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def save(self):
        data = self.data.copy()
        wifi = data.pop('wifi', None)

        write_json_to_file(CONFIG_PATH, data)
        if wifi is not None:
            write_json_to_file(WIFI_PATH, wifi)


@singleton
class TokenStore(object):
    def __init__(self):
        self.secret = None
        self.data = {}

        if exists(SECRETS_PATH):
            self.secret = load_json_from_file(SECRETS_PATH)['token_secret']
        else:
            self.secret = generate_random_string()
            write_json_to_file(SECRETS_PATH, {'token_secret': self.secret})

        if exists(TOKENS_PATH):
            self.data = load_json_from_file(TOKENS_PATH)

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def create_token(self, client_id):
        token = generate_bearer_token(self.secret)
        self.data[client_id] = token

        return token

    def save(self):
        data = self.data
        write_json_to_file(TOKENS_PATH, data)


conf = Config()
tokenstore = TokenStore()
