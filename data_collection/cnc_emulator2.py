"""
CNC server emulation with multiple connections support.
"""

import socket
import random
import threading

HOST = 'localhost'
PORT = 9999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(100)


def handler(c):
    while 1:
        data = c.recv(1024)
        print(data.decode('utf8'))
        rand_float = f'{random.randint(1, 99)}.{random.randint(0, 999)}'
        rand_sign = f"{random.choice(['-', ''])}"
        c.sendall(bytes(f'>>MACRO, {rand_sign}{rand_float}\r', encoding='utf8'))


def main():
    while True:
        # Wait for client
        client, addr = s.accept()
        print('# Connected to ' + addr[0] + ':' + str(addr[1]))

        # Receive data from client
        t = threading.Thread(target=handler, args=(client, ))
        t.start()


if __name__ == '__main__':
    main()