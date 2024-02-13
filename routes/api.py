import machine
import gc

from config import conf, pinSMO, pinDMO, pinMSW, autosave
from lib.picoweb import jsonify, start_response


def update(request, response):
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


def get_config(request, response):
    """
    Get the config
    """
    nconfig = conf.data
    nconfig['network']['password'] = '**************************'

    yield from start_response(response, content_type="application/octet-stream")
    yield from jsonify(response, nconfig)


def get_settings_mode(request, response):
    """
    Get the actual mode (single or double)
    """
    yield from jsonify(response, conf.data)


def get_single_duration(request, response):
    """
    Get the duration of a single shot
    """
    yield from jsonify(response, conf.data)


def set_single_duration(request, response):
    """
    Set the duration of a single shot
    """
    yield from request.read_form_data()
    conf.data['grinder']['single'] = request.form.get('duration')
    gc.collect()
    yield from jsonify(response, conf.data)


def get_double_duration(request, response):
    """
    Get the duration of a double shot
    """
    yield from jsonify(response, conf.data)


def set_double_duration(request, response):
    """
    Set the duration of a single shot
    """
    yield from request.read_form_data()
    conf.data['grinder']['double'] = request.form.get('duration')
    gc.collect()
    yield from jsonify(response, conf.data)


def get_memorize_timeout(request, response):
    """
    Get how long a started grind will be memorized
    """
    yield from jsonify(response, conf.data)


def set_memorize_timeout(request, response):
    """
    Set how long a started grind will be memorized
    """
    yield from request.read_form_data()
    conf.data['grinder']['memorize_timeout'] = request.form.get('memorize_timeout')
    gc.collect()
    yield from jsonify(response, conf.data)


def get_stats_grinds_single(request, response):
    """
    Get the total amount of single shots grinded
    """
    yield from jsonify(response, conf.data)


def get_stats_grinds_double(request, response):
    """
    Get the total amount of single shots grinded
    """
    yield from jsonify(response, conf.data)


def reset_stats(request, response):
    """
    Reset the statistics
    """
    conf.reset()
    yield from jsonify(response, conf.data)


def reset_machine(request, response):
    """
    Reset the machine
    """
    machine.reset()
