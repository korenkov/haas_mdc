"""
CNC server emulation with multiple connections support.
"""

import socket
import random
import threading
import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    '--host', type=str, help='cnc emulator bind host',
    default='localhost', required=False
)
parser.add_argument(
    '--port', type=str, help='cnc emulator bind port',
    default=9999, required=False
)
args = parser.parse_args()

HOST = args.host
PORT = args.port


class Server:
    def __init__(self, host, port, listen=10, name='Server'):
        self.host = host
        self.port = port
        self.name = name
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))
        self.s.listen(listen)
        self.client = None

    def log(self, message):
        print(f'[{self.name} {self.host}:{self.port}] {message}')

    def handle(self):
        while 1:
            data = self.client.recv(1024)
            self.log(data.decode('utf8'))
            rand_float = f'{random.randint(1, 99)}.{random.randint(0, 999)}'
            rand_sign = f"{random.choice(['-', ''])}"
            self.client.sendall(
                bytes(f'>>MACRO, {rand_sign}{rand_float}\r', encoding='utf8'))

    def start(self):
        self.log(f'\n--- started ---\n')
        while 1:
            self.client, addr = self.s.accept()
            print(addr)
            t = threading.Thread(target=self.handle, args=())
            t.start()


if __name__ == '__main__':
    Server(HOST, PORT).start()
