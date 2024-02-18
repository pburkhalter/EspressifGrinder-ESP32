import asyncio
import ssl

from lib.microdot import Microdot
from lib.aswitch import Switch
from lib.aswitch import Pushbutton

from config import conf, pinSMO, pinDMO, pinMSW
from grinder import GrinderController

import routes.init as init_routes
import routes.web as web_routes
import routes.api as api_routes


def setup_switches(grinder):
    # Setup hardware switches and pushbutton with their functionalities
    smo_switch = Switch(pinSMO)
    smo_switch.close_func(lambda: grinder.set_mode("single"))

    dmo_switch = Switch(pinDMO)
    dmo_switch.close_func(lambda: grinder.set_mode("double"))

    msw_button = Pushbutton(pinMSW)
    msw_button.press_func(grinder.start_grinding)
    msw_button.release_func(grinder.stop_grinding)


def register_routes(app):
    routes = [
        ('/',                               web_routes.index,                   ['GET']),
        ('/api/update',                     api_routes.update,                  ['GET']),
        ('/api/configs',                     api_routes.get_config,              ['GET']),
        ('/api/grinder/mode',               api_routes.get_settings_mode,       ['GET']),
        ('/api/grinder/single/duration',    api_routes.get_single_duration,     ['GET']),
        ('/api/grinder/single/duration',    api_routes.set_single_duration,     ['POST']),
        ('/api/grinder/double/duration',    api_routes.get_double_duration,     ['GET']),
        ('/api/grinder/double/duration',    api_routes.set_double_duration,     ['POST']),
        ('/api/grinder/memorize/timeout',   api_routes.get_memorize_timeout,    ['GET']),
        ('/api/grinder/memorize/timeout',   api_routes.set_memorize_timeout,    ['POST']),
        ('/api/stats/grinds/single',        api_routes.get_stats_grinds_single, ['GET']),
        ('/api/stats/grinds/double',        api_routes.get_stats_grinds_double, ['GET']),
        ('/api/stats/reset',                api_routes.reset_stats,             ['GET']),
        ('/api/machine/reset',              api_routes.reset_machine,           ['GET']),
    ]

    for path, handler, methods in routes:
        app.route(path, methods=methods)(handler)


def register_init_routes(app):
    routes = [
        ('/api/init/status',   init_routes.get_init_status,       ['GET']),
        ('/api/init/reset',    init_routes.get_reset_setup,       ['GET']),
        ('/api/init/device',   init_routes.get_device_info,       ['GET']),
        ('/api/init/finish',   init_routes.get_finish,            ['GET']),
        ('/api/init/register', init_routes.post_register_device,  ['POST']),
        ('/api/init/wifi',     init_routes.post_wifi_credentials, ['POST']),
        ('/api/init/cert',     init_routes.upload_certificate,    ['POST']),
        ('/api/init/key',      init_routes.upload_key,            ['POST']),
    ]

    for path, handler, methods in routes:
        app.route(path, methods=methods)(handler)


async def main():
    print("Starting application...")

    # Initialize the Microdot server
    app = Microdot()

    if conf['general']['initialized']:
        # Initialize the Grinder Controller
        grinder = GrinderController()

        # Setup hardware controls
        setup_switches(grinder)

        # Register web routes
        register_routes(app)
    else:
        # Register init web routes
        register_init_routes(app)

    # Start the web server if REST API is enabled
    if conf['general']['initialized'] and conf['api']['enable']:
        host = conf['api']['host']
        port = conf['api']['port']

        sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        sslctx.load_cert_chain(
            certfile='./secrets/certs/cert.der',
            keyfile='./secrets/certs/key.der'
        )

        app.run(host=host, port=port, ssl=sslctx)
    else:
        app.run(host='0.0.0.0', port=80)


# Run the application
if __name__ == "__main__":
    asyncio.run(main())
