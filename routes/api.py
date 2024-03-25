import asyncio
import json
import machine

from config import conf, tokens
from lib.microdot import Response
from routes.decorators import require_content_type, require_auth


@require_auth()
def get_config(request):
    c = conf['data']
    c['wifi']['password'] = 10 * '*'
    return Response(json.dumps(c), status_code=200)


@require_auth()
def get_status(request):
    print(conf['general']['initialized'])
    return Response('OK', status_code=200)


@require_auth()
def get_factory_reset(request):
    conf['general']['initialized'] = False
    conf.save()

    async def delayed_reset():
        await asyncio.sleep(2)
        machine.reset()

    asyncio.create_task(delayed_reset())
    return Response('OK', status_code=200)


@require_auth()
def get_reboot_machine(request):
    async def delayed_reset():
        await asyncio.sleep(2)
        machine.reset()

    asyncio.create_task(delayed_reset())
    return Response(status_code=200)


@require_auth()
@require_content_type('application/json')
def post_config(request):
    if not conf.load(request.json):
        return Response(status_code=500)
    return Response(status_code=200)


@require_auth()
@require_content_type('text/plain')
def post_modeset(request):
    mode = request.body
    if not mode:
        return Response('Bad Request: Missing "mode"', status_code=400)

    valid_modes = ['grind', 'learn']
    if mode not in valid_modes:
        return Response('Invalid mode', status_code=400)

    conf['modeset'] = mode
    return Response(status_code=200)


@require_auth()
def get_enable_register(request):
    tokens.enable_register(timeout=300)
    return Response(status_code=200)


@require_auth()
@require_content_type('text/plain')
def post_register_device(request):
    client_id = request.body
    if not client_id:
        return Response('Bad Request: Missing client id', status_code=400)

    token = tokens.create_token(client_id)
    tokens.save()

    return Response(token, status_code=200)
