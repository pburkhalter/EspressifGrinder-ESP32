import gc
import os
import esp
import network
import machine
import math
import ubinascii
import utime
import uasyncio

from lib.picoweb import WebApp, start_response
from lib.aswitch import Switch
from lib.aswitch import Pushbutton

from config import conf, pinSMO, pinDMO, pinMSW, autosave
from grinder import GrinderController

import routes.api as api_routes


# Initialize the WebApp
webapp = WebApp(__name__)
webapp._load_template('index.tpl')  # Preload templates to avoid memory issues
gc.collect()

# Initialize the Grinder Controller
grinder = GrinderController()


def setup_switches():
    # Setup hardware switches and pushbutton with their functionalities
    smo_switch = Switch(pinSMO)
    smo_switch.close_func(lambda: grinder.set_mode("single"))

    dmo_switch = Switch(pinDMO)
    dmo_switch.close_func(lambda: grinder.set_mode("double"))

    msw_button = Pushbutton(pinMSW)
    msw_button.press_func(grinder.start_grinding)
    msw_button.release_func(grinder.stop_grinding)


def register_routes():
    # Register all routes for the web application
    routes = [
        ('/api/update',                     api_routes.update,                  'GET'),
        ('/api/config',                     api_routes.get_config,              'GET'),
        ('/api/grinder/mode',               api_routes.get_settings_mode,       'GET'),
        ('/api/grinder/single/duration',    api_routes.get_single_duration,     'GET'),
        ('/api/grinder/single/duration',    api_routes.set_single_duration,     'POST'),
        ('/api/grinder/double/duration',    api_routes.get_double_duration,     'GET'),
        ('/api/grinder/double/duration',    api_routes.set_double_duration,     'POST'),
        ('/api/grinder/memorize/timeout',   api_routes.get_memorize_timeout,    'GET'),
        ('/api/grinder/memorize/timeout',   api_routes.set_memorize_timeout,    'POST'),
        ('/api/stats/grinds/single',        api_routes.get_stats_grinds_single, 'GET'),
        ('/api/stats/grinds/double',        api_routes.get_stats_grinds_double, 'GET'),
        ('/api/stats/reset',                api_routes.reset_stats,             'GET'),
        ('/api/machine/reset',              api_routes.reset_machine,           'GET'),
    ]

    for path, handler, method in routes:
        webapp.route(path, method=method)(handler)


@webapp.route('/', method='GET')
def index(request, response):
    sta_if = network.WLAN(network.STA_IF)
    network_config = sta_if.ifconfig()
    device_infos = os.uname()
    infos = {
        "device_description": conf.data['general']['description'],
        "device_model": device_infos[4],
        "device_firmware": device_infos[3],
        "device_freemem": math.floor(gc.mem_free() / 1000),
        "device_totalspace": math.floor(esp.flash_size() / 1000000),
        "device_uptime": math.floor(utime.ticks_ms() / 1000000000),
        "device_cpufreq": machine.freq() / 1000000,
        "network_connected": sta_if.isconnected(),
        "network_ssid": sta_if.config('ssid'),
        "network_hostname": network.hostname,
        "network_ip": network_config[0],
        "network_subnet": network_config[1],
        "network_gateway": network_config[2],
        "network_dns": network_config[3],
        "network_mac": ubinascii.hexlify(network.WLAN().config('mac'), ':').decode(),
        "grind_autosave": conf.data['general']['autosave_timeout'],
        "grind_single_duration": conf.data['grinder']['single'],
        "grind_double_duration": conf.data['grinder']['double'],
        "grind_memorize_timeout": conf.data['grinder']['memorize_timeout'],
        "stats_grinds_single": conf.data['stats']['single'],
        "stats_grinds_double": conf.data['stats']['double'],
        "stats_grinds_total_time": conf.data['stats']['duration'],
    }

    yield from start_response(response, content_type="text/html")
    yield from webapp.render_template(response, 'index.tpl', (infos,))


async def main():
    print("Starting application...")

    # Setup hardware controls
    setup_switches()

    # Register web routes
    register_routes()

    # Setup autosave if configured
    if conf.data.get('general', {}).get('autosave_timeout', 0) > 0:
        uasyncio.create_task(autosave(conf.data['general']['autosave_timeout']))

    # Start the web server if REST API is enabled
    if conf.data.get('network', {}).get('enable_restapi', True):
        host = conf.data['network'].get('host', '0.0.0.0')
        port = conf.data['network'].get('port', 80)
        debug = conf.data['network'].get('debug', False)
        uasyncio.create_task(webapp.run(host, port, debug=debug))

    # Collect garbage to free up unused memory
    gc.collect()

    # Keep the server running
    while True:
        await uasyncio.sleep(1)


# Run the application
if __name__ == "__main__":
    uasyncio.run(main())
