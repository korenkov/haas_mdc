import threading

from data_collection.cnc_emulator2 import Server
from data_collection.main import parse_configs


def main():
    configs = parse_configs()

    def start_server():
        Server(host, port, name=machine_id).start()

    for machine_id, conf in configs.items():
        host = conf.get('host')
        port = int(conf.get('port'))

        if host and port:
            # start server
            t = threading.Thread(target=start_server, args=())
            t.start()


if __name__ == '__main__':
    main()
