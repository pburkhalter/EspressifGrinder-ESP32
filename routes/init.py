import asyncio
import time

import ubinascii
import machine
import json
from lib.microdot import Response
from lib.pathutils import ensure_dir_exists

from config import conf, tokens
from routes.decorators import require_content_type


def get_status(request):
    return Response(conf['general']['initialized'], status_code=200)


def get_device_info(request):
    return Response(json.dumps(conf), status_code=200)


def get_finish(request):
    async def delayed_reset():
        await asyncio.sleep(2)
        machine.reset()

    conf['general']['initialized'] = True
    conf.save()

    asyncio.create_task(delayed_reset())

    return Response(status_code=200)


def get_factory_reset(request):
    conf['general']['initialized'] = False
    conf.save()
    return Response('OK', status_code=200)


@require_content_type('text/plain')
def upload_certificate(request):
    try:
        file_content = ubinascii.a2b_base64(request.body)
        directory = '/secrets/certs'
        ensure_dir_exists(directory)

        with open('/secrets/certs/cert.der', 'wb') as f:
            f.write(file_content)

        return Response(status_code=200)
    except Exception as e:
        print('Error saving the certificate:', e)
        return Response('Internal Server Error', status_code=500)


@require_content_type('text/plain')
def upload_key(request):
    try:
        file_content = ubinascii.a2b_base64(request.body)
        directory = '/secrets/certs'
        ensure_dir_exists(directory)

        with open('/secrets/certs/key.der', 'wb') as f:
            f.write(file_content)

        return Response(status_code=200)
    except Exception as e:
        print('Error saving the key:', e)
        return Response('Internal Server Error', status_code=500)


@require_content_type('application/json')
def post_wifi_credentials(request):
    try:
        json_data = request.json
        ssid = json_data.get('ssid')
        password = json_data.get('password')

        if not ssid or not password:
            print("Did not provide SSID and password")
            return Response('Bad Request: Missing "ssid" or "password"', status_code=400)

        conf['wifi'] = {'ssid': ssid, 'password': password}
        conf.save()

        return Response(status_code=200)
    except Exception as e:
        print('Error saving the wifi credentials:', e)
        return Response('Internal Server Error', status_code=500)


@require_content_type('text/plain')
def post_register_client(request):
    client_id = request.body
    if not client_id:
        return Response('Bad Request: Missing client id', status_code=400)

    token = tokens.create_token(client_id)
    tokens.save()

    return Response(token, status_code=200)

