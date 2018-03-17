import socketserver
import random

class CncMachineEmulator(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request.recv(1024).strip()
        print(f'{self.client_address[0]} wrote:')
        print(data)

        # just send back the same data, but upper-cased
        rand_float = f'{random.randint(1, 9)}.{random.randint(0, 999)}'
        rand_sign = f"{random.choice(['-', ''])}"
        self.request.sendall(bytes(f'>>MACRO, {rand_sign}{rand_float}\r', encoding='utf8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), CncMachineEmulator) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
