import os
import time
import datetime
import configparser
import collections
import threading
import telnetlib

import re


BASE_DIR = os.path.dirname(__file__)

SECOND = 's'
MINUTE = 'm'
HOUR = 'h'
DAY = 'D'
WEEK = 'W'

# parsing param value string
# for example: ">>MACRO, -182.633216" -> -182.633
PARAM_RE = re.compile('[-+]?[0-9]*\.?[0-9]+', re.IGNORECASE)
PARAM_PRECISION = 3

# storage for threads with jobs
thread_list = []


def parse_param(text):
    return round(float(PARAM_RE.findall(text)[0]), PARAM_PRECISION)


def save_param(machine_id, code, value):
    """Save param to database."""
    raise NotImplemented()


class Param:
    #: parsing param value string
    #: for example: ">>MACRO, -182.633216" -> -182.633
    PARAM_RE = re.compile('[-+]?[0-9]*\.?[0-9]+', re.IGNORECASE)
    PRECISION = 3

    def __init__(self, name, command):
        self.name = name        # custom name of macro variable (for example: "x")
        self.command = command  # 4-digit macro variable number (for example: "5021")
        self.value = None       # result of measuring (for example: 182.633)

    @staticmethod
    def parse(self, text):
        self.value = round(float(self.PARAM_RE.findall(text)[0]), self.PRECISION)


def parse_configs():
    # path to the configs directory
    CONFIGS_DIR = os.path.join(BASE_DIR, 'configs')

    network_config = configparser.ConfigParser()
    params_config = configparser.ConfigParser()
    params_config.read(os.path.join(CONFIGS_DIR, 'params.ini'))
    network_config.read(os.path.join(CONFIGS_DIR, 'network.ini'))

    # map for storing configs for all machines
    # key: machine unique identifier, value: machine configs
    configs = collections.defaultdict(dict)

    # parse network config
    for section in network_config.sections():
        for item in network_config[section].items():
            configs[section][item[0]] = item[1]

    # parse params config
    for section in params_config.sections():
        _params = {}
        for item in params_config[section].items():
            code, interval_str = item
            interval, interval_type = interval_str[:-1], interval_str[-1:]
            _params[code] = {'interval_value': int(interval),
                             'interval_type': interval_type}

            configs[section]['params'] = _params

    return configs


def start_measuring(machine_id, code, configs, interval_seconds):
    host = configs[machine_id].get('host')
    port = configs[machine_id].get('port')

    while 1:
        print(f'{datetime.datetime.now()}: {code}, cnc: {machine_id}')
        time.sleep(interval_seconds)

    # with telnetlib.Telnet(host, port) as tn:
    #     while 1:
    #         # write to socket
    #         tn.write(f'?Q600 {code}\r')
    #
    #         # retrieve data from socket
    #         val = parse_param(tn.read_until('\r'))
    #
    #         print(f'{datetime.datetime.now()}: {code}, '
    #               f'cnc: {machine_id}, value: {val}')


def schedule_measuring(interval_value, interval_type,
                       machine_id, code, configs):
    if interval_type == SECOND:
        inter = interval_value
    elif interval_type == MINUTE:
        inter = interval_value * 60
    elif interval_type == HOUR:
        inter = interval_value * 60 * 60
    elif interval_type == DAY:
        inter = interval_value * 60 * 60 * 24
    elif interval_type == WEEK:
        inter = interval_value * 60 * 60 * 24 * 7
    else:
        raise Exception(f'{interval_type} is unsupported interval type')

    thread_list.append(
        threading.Thread(target=start_measuring,
                         args=(machine_id, code, configs, inter))
    )


def schedule_tasks(configs):
    for machine_id, machine_configs in configs.items():
        params = machine_configs.get('params')
        if not params:
            continue

        for param_code, interval in params.items():
            print(param_code, interval.get('interval_value'), interval.get('interval_type'))

            schedule_measuring(
                interval.get('interval_value'), interval.get('interval_type'),
                machine_id, param_code, configs
            )


def run_tasks():
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()


def main():
    # retrieve configs
    configs = parse_configs()

    # schedule tasks
    schedule_tasks(configs)

    # run scheduled tasks
    run_tasks()


if __name__ == '__main__':
    main()
