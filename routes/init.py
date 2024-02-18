import ubinascii
import machine
import json
from lib.microdot import Response
from lib.pathutils import ensure_dir_exists

from config import conf, tokenstore


def get_init_status(request):
    response = Response('OK', status_code=200)
    return response


def get_device_info(request):
    response = Response(json.dumps(conf), status_code=200)
    return response


def get_finish(request):
    conf['general']['initialized'] = True
    conf.save()
    machine.reset()


def get_reset_setup(request):
    # TODO
    pass


def upload_certificate(request):
    content_type = request.headers.get('Content-Type')

    if content_type != 'text/plain; charset=utf-8':
        return 'Unsupported Media Type', 415

    try:
        file_content = ubinascii.a2b_base64(request.body)
        directory = '/secrets/certs'
        ensure_dir_exists(directory)

        with open('/secrets/certs/cert.der', 'wb') as f:
            f.write(file_content)

        return 'OK', 200
    except Exception as e:
        print('Error saving the certificate:', e)
        return 'Internal Server Error', 500


def upload_key(request):
    content_type = request.headers.get('Content-Type')

    if content_type != 'text/plain; charset=utf-8':
        return 'Unsupported Media Type', 415

    try:
        file_content = ubinascii.a2b_base64(request.body)
        directory = '/secrets/certs'
        ensure_dir_exists(directory)

        with open('/secrets/certs/key.der', 'wb') as f:
            f.write(file_content)

        return 'OK', 200
    except Exception as e:
        print('Error saving the key:', e)
        return 'Internal Server Error', 500


def post_wifi_credentials(request):
    content_type = request.headers.get('Content-Type')

    if content_type != 'application/json; charset=UTF-8':
        return 'Unsupported Media Type', 415

    try:
        json_data = request.json
        ssid = json_data.get('ssid')
        password = json_data.get('password')

        if not ssid or not password:
            print("Did not provide SSID and password")
            return Response('Bad Request: Missing "ap" or "pw"', status_code=400)

        conf['wifi'] = {'ssid': ssid, 'password': password}
        conf.save()

        return Response('OK', status_code=200)
    except Exception as e:
        print('Error saving the wifi credentials:', e)
        return Response('Internal Server Error', status_code=500)


def post_register_device(request):
    content_type = request.headers.get('Content-Type')

    if content_type != 'text/plain; charset=UTF-8':
        return 'Unsupported Media Type', 415

    client_id = request.body

    if not client_id:
        return Response('Bad Request: Missing "clientId"', status_code=400)

    token = tokenstore.create_token(client_id)
    tokenstore.save()

    return Response(token, status_code=200)

