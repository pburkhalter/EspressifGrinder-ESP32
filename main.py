import uasyncio
import network
import machine
import gc
import esp
import os
import utime
import micropython
import math
import ubinascii

from config import conf, pinD5, pinD6, pinD7, autosave
from picoweb import WebApp, jsonify, start_response
from aswitch.aswitch import Switch
from aswitch.abutton import Pushbutton
from grinder import GrinderController


# Pico web server
webapp = WebApp(__name__)

# Preload templates to avoid memory fragmentation issues
webapp._load_template('index.tpl')
gc.collect()

# Coffee Grinder Controller
grinder = GrinderController()


def switch_single():
    grinder.set_mode("single")


def switch_double():
    grinder.set_mode("double")


def button_grind_press():
    grinder.start()


def button_grind_release():
    grinder.stop()


# Routes
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
        "network_ssid": sta_if.config('essid'),
        "network_rssi": sta_if.status('rssi'),
        "network_hostname": sta_if.config('dhcp_hostname'),
        "network_ip": network_config[0],
        "network_subnet": network_config[1],
        "network_gateway": network_config[2],
        "network_dns": network_config[3],
        "network_mac": ubinascii.hexlify(network.WLAN().config('mac'),':').decode(),
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

@webapp.route("/update")
def index(request, response):
    if request.method == "POST":
        yield from request.read_form_data()
    else:  # GET, apparently
        # Note: parse_qs() is not a coroutine, but a normal function.
        # But you can call it using yield from too.
        request.parse_qs()

    # Whether form data comes from GET or POST request, once parsed,
    # it's available as req.form dictionary
    conf.data['grinder']['single'] = int(request.form["single"])
    conf.data['grinder']['double'] = int(request.form["double"])
    conf.data['grinder']['memorize_timeout'] = int(request.form["timeout"])
    conf.write()

    # redirect to "/"
    headers = {"Location": "/"}
    yield from start_response(response, status="303", headers=headers)

@webapp.route('/config', method='GET')
def grind(request, response):
    """
    Get the config
    """
    nconfig = conf.data
    nconfig['network']['password'] = '**************************'

    yield from start_response(response, content_type="application/octet-stream")
    yield from jsonify(response, nconfig)

@webapp.route('/settings/mode', method='GET')
def get_settings_mode(request, response):
    """
    Get the actual mode (single or double)
    """
    yield from jsonify(response, conf.data)


@webapp.route('/settings/single/duration', method='GET')
def get_single_duration(request, response):
    """
    Get the duration of a single shot
    """
    yield from jsonify(response, conf.data)


@webapp.route('/settings/single/duration', method='POST')
def set_single_duration(request, response):
    """
    Set the duration of a single shot
    """
    yield from request.read_form_data()
    conf.data['grinder']['single'] = request.form.get('duration')
    gc.collect()
    yield from jsonify(response, conf.data)


@webapp.route('/settings/double/duration', method='GET')
def get_double_duration(request, response):
    """
    Get the duration of a double shot
    """
    yield from jsonify(response, conf.data)


@webapp.route('/settings/double/duration', method='POST')
def set_double_duration(request, response):
    """
    Set the duration of a single shot
    """
    yield from request.read_form_data()
    conf.data['grinder']['double'] = request.form.get('duration')
    gc.collect()
    yield from jsonify(response, conf.data)


@webapp.route('/settings/memorize/timeout', method='GET')
def get_memorize_timeout(request, response):
    """
    Get how long a started grind will be memorized
    """
    yield from jsonify(response, conf.data)


@webapp.route('/settings/memorize/timeout', method='POST')
def set_memorize_timeout(request, response):
    """
    Set how long a started grind will be memorized
    """
    yield from request.read_form_data()
    conf.data['grinder']['memorize_timeout'] = request.form.get('memorize_timeout')
    gc.collect()
    yield from jsonify(response, conf.data)


@webapp.route('/stats/grinds/single', method='GET')
def get_stats_grinds_single(request, response):
    """
    Get the total amount of single shots grinded
    """
    yield from jsonify(response, conf.data)


@webapp.route('/stats/grinds/double', method='GET')
def get_stats_grinds_double(request, response):
    """
    Get the total amount of single shots grinded
    """
    yield from jsonify(response, conf.data)


@webapp.route('/stats/reset', method='GET')
def reset_stats(request, response):
    """
    Reset the statistics
    """
    conf.reset()
    yield from jsonify(response, conf.data)

@webapp.route('/machine/reset', method='GET')
def reset_machine(request, response):
    """
    Reset the machine
    """
    import machine
    machine.reset()


async def main():
    print("Starting...")

    ps = Switch(pinD5)
    pd = Switch(pinD6)
    pg = Pushbutton(pinD7)
    
    ps.close_func(switch_single)
    pd.close_func(switch_double)
    pg.press_func(button_grind_press)
    pg.release_func(button_grind_release)
    
    loop = uasyncio.get_event_loop()

    if conf.data['general']['autosave_timeout'] > 0:
        loop.create_task(autosave(conf.data['general']['autosave_timeout']))

    if conf.data['network']['enable_restapi'] is True:
        loop.create_task(webapp.run(
            conf.data['network']['host'],
            conf.data['network']['port'],
            debug=True)
        )

    gc.collect()
    loop.run_forever()


uasyncio.run(main())
