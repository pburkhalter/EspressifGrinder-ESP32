import binascii
import hashlib
import os
import json
from machine import Pin

from lib.secret import generate_random_string
from lib.singleton import singleton


# Pin mapping
pinSMO = Pin(33, Pin.IN, Pin.PULL_UP)   # Single Mode
pinDMO = Pin(32, Pin.IN, Pin.PULL_UP)   # Double Mode
pinGRN = Pin(25, Pin.OUT, Pin.PULL_UP)  # Grinder
pinLED = Pin(26, Pin.OUT, Pin.PULL_UP)  # LED
pinMSW = Pin(27, Pin.IN, Pin.PULL_UP)   # Microswitch


WIFI_PATH = './secrets/tokens.json'
TOKENS_PATH = './secrets/tokens.json'
CONFIG_PATH = 'configs/configs.json'
CONFIG_DEFAULT_PATH = 'configs/config.default.json'


def exists(path):
    try:
        directory, filename = path.rsplit('/', 1)
    except ValueError:
        # No '/' in path, implying current directory
        directory, filename = '.', path

    try:
        # Checking in the specified directory
        for entry in os.ilistdir(directory):
            if entry[0] == filename:
                return True
        return False
    except OSError:
        # OSError implies the directory doesn't exist, so the file/dir doesn't exist
        return False


def ensure_dir_exists(directory):
    # Split the directory path to check each part and create if necessary
    parts = directory.split('/')
    path = ''
    for part in parts:
        if part:  # Ignore empty parts to handle leading '/'
            path += '/' + part if path else part
            if not exists(path):
                try:
                    os.mkdir(path)
                except OSError as e:
                    print(f"Failed to create directory {path}: {e}")


def load_json_from_file(filepath):
    try:
        f = open(filepath, 'r')
        data = json.loads(f.read())
        f.close()
        return data

    except (OSError, KeyError, ValueError, FileNotFoundError):
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
        object.__setattr__(self, 'data', {})

        if not exists(CONFIG_PATH) or not load_json_from_file(CONFIG_PATH):
            print("No configs file found. Creating from default configs file...")
            write_json_to_file(CONFIG_PATH, load_json_from_file(CONFIG_DEFAULT_PATH))

        if exists(CONFIG_PATH):
            object.__setattr__(self, 'data', load_json_from_file(CONFIG_PATH))

        if exists(WIFI_PATH):
            self.data['wifi'] = load_json_from_file(WIFI_PATH)

    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{item}'")

    def __setattr__(self, key, value):
        if key == 'data':
            object.__setattr__(self, key, value)
        else:
            self.data[key] = value

    def __delattr__(self, item):
        if item in self.data:
            del self.data[item]
        else:
            object.__delattr__(self, item)

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
        self.data = {}

        if exists(TOKENS_PATH):
            self.data = load_json_from_file(TOKENS_PATH)

    def __getattr__(self, item):
        try:
            return self.data[item]
        except KeyError:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{item}'")

    def __setattr__(self, key, value):
        if key == 'data':
            object.__setattr__(self, key, value)
        else:
            self.data[key] = value

    def __delattr__(self, item):
        if item in self.data:
            del self.data[item]
        else:
            object.__delattr__(self, item)

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def create_token(self, client_id):
        token = hashlib.sha256(client_id + generate_random_string())
        self.data[client_id] = binascii.hexlify(token.digest())
        return token

    def save(self):
        data = self.data
        write_json_to_file(TOKENS_PATH, data)


conf = Config()
tokenstore = TokenStore()
