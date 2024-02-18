import time
import uos
from lib import jwt


def generate_random_string(length=64):
    source = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    return ''.join(source[uos.urandom(1)[0] % len(source)] for _ in range(length))


def generate_bearer_token(secret):
    iat = int(time.time())
    exp = iat + (3650 * 24 * 60 * 60)  # 3650 days in seconds

    payload = {
        'iat': iat,
        'exp': exp,
        'sub': 'access_token'
    }

    secret_bytes = secret.encode('utf-8')

    token = jwt.encode(payload, secret_bytes, algorithm='HS256')
    return token
