import json
import os

import machine
from lib.microdot import Response

from config import conf, tokenstore


def get_init_status(request):
    response = Response('OK', status_code=200)
    return response


def get_finish(request):
    conf['general']['initialized'] = True

    response = Response('OK', status_code=200)
    return response


def upload_certificate(request):
    content_type = request.headers.get('Content-Type')
    if content_type != 'text/plain':
        return Response('Unsupported Media Type', 415)

    try:
        file_content = request.body

        directory = '/secrets/certs'
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open('/secrets/certs/cert.der', 'wb') as f:
            f.write(file_content)

        return Response('OK', status_code=200)
    except Exception as e:
        print(f'Error saving the certificate: {e}')
        return Response('Internal Server Error', status_code=500)


def upload_key(request):
    content_type = request.headers.get('Content-Type')
    if content_type != 'text/plain':
        return Response('Unsupported Media Type', 415)

    try:
        file_content = request.body

        directory = '/secrets/certs'
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open('/secrets/certs/key.der', 'wb') as f:
            f.write(file_content)

        return Response('OK', status_code=200)
    except Exception as e:
        print(f'Error saving the certificate: {e}')
        return Response('Internal Server Error', status_code=500)


def post_wifi_credentials(request):
    if not request.json:
        return Response('Bad Request: JSON body required', status_code=400)

    ssid = request.json.get('ap')
    password = request.json.get('pw')

    if not ssid or not password:
        return Response('Bad Request: Missing "ap" or "pw"', status_code=400)

    conf['wifi']['ssid'] = ssid
    conf['wifi']['password'] = password
    conf.save()

    return Response('OK', status_code=200)


def post_register_device(request):
    if not request.json:
        return Response('Bad Request: JSON body required', status_code=400)

    client_id = request.json.get('clientId')

    if not client_id:
        return Response('Bad Request: Missing "clientId"', status_code=400)

    token = tokenstore.create_token(client_id)
    tokenstore.save()

    return Response(token, status_code=200)


def get_reset(request):
    machine.reset()


