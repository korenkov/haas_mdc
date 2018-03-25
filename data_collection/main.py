import os
import re
import time
import datetime
import configparser
import collections
import threading
import telnetlib
import sqlite3


BASE_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_DB_PATH = os.path.join(PROJECT_DIR, 'data.db')

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


def get_cursor():
    active_thread = threading.local()
    cursor = getattr(active_thread, '_cursor', None)
    conn = getattr(active_thread, '_conn', None)
    if not cursor:
        # print('create new connection to DB ...')
        conn = sqlite3.connect(DATA_DB_PATH)
        cursor = conn.cursor()
        active_thread._cursor = cursor
        active_thread._conn = conn
    return conn, cursor


def save_param(log_date, param_code, param_val, machine_id):
    """Save param to database."""
    conn, c = get_cursor()
    sql = f"""
    insert into params_data(log_date, param_code, param_val, machine_id) 
    values ({log_date}, {param_code}, {param_val}, '{machine_id}');
    """
    c.execute(sql)
    conn.commit()


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

    def _process():
        # write to socket
        tn.write(bytes(f'?Q600 {code}\r', encoding='utf8'))

        # retrieve data from socket
        bytes_data = tn.read_until(bytes('\r', encoding='utf8'))
        val = parse_param(str(bytes_data))

        print(f'{datetime.datetime.now()}: {code}, '
              f'cnc: {machine_id}, value: {val}')

        save_param(time.time(), code, val, machine_id)

        time.sleep(interval_seconds)

    try:
        with telnetlib.Telnet(host, port, timeout=5) as tn:
            while 1:
                try:
                    _process()
                except (ConnectionResetError, ConnectionAbortedError, EOFError) as e:
                    print(f'[{host}:{port}] {e}')
                    print('reconnecting ...')
                    start_measuring(machine_id, code, configs, interval_seconds)

    except ConnectionRefusedError as e:
        print(f'[{host}:{port}] {e}')


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
                machine_id, param_code, configs)


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
