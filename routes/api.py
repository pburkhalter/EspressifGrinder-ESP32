import json

from config import conf


def get_config(request):
    c = conf.data
    c['wifi']['password'] = 10 * '*'

    return json.dumps(c), 200, {'Content-Type': 'application/json'}


def get_reset(request):
    pass


def get_device(request):
    pass


def update(request):
    pass


def get_settings_mode(request):
    pass


def get_single_duration(request):
    pass


def set_single_duration(request):
    pass


def get_double_duration(request):
    pass


def set_double_duration(request):
    pass


def get_memorize_timeout(request):
    pass


def set_memorize_timeout(request):
    pass


def get_stats_grinds_single(request):
    pass


def get_stats_grinds_double(request):
    pass


def reset_stats(request):
    pass


def reset_machine(request):
    pass
