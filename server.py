from socket import socket, AF_INET, SOCK_STREAM, SO_REUSEADDR, SOL_SOCKET
from threading import Thread
from textwrap import dedent
from sys import stdin, exit
from getpass import getuser
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from struct import pack, unpack

VERSION = 'v0.0.1'


# server class
class Server:
    def __init__(self, host, port, two_way):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.clients = []
        self.two_way_conn = two_way
        self.user = getuser()

    def start(self):
        self.server.bind((self.host, self.port))
        print(f'[+] Listening on {self.host}:{self.port}.')
        self.server.listen()

        if not self.two_way_conn:
            t = Thread(target=self.one_way)
            t.start()

        while True:
            try:
                conn, addr = self.server.accept()
                user = self.recv_full(conn)

                self.update_clients(conn)
                print(f'[+] Client connected from {addr[0]}:{addr[1]} with username {user}.')
                self.send_full(conn, 'Two-Way Connection' if self.two_way_conn else 'One-Way Connection')

                if self.two_way_conn:
                    t = Thread(target=self.two_way, args=(conn, user))
                    t.start()
            
            except KeyboardInterrupt:
                print('[*] Server shutting down...')
                self.server.close()
                exit(0)
            
        self.server.close()
        exit(0)

    def update_clients(self, conn):
        self.clients.append(conn)

    def one_way(self):
        while True:
            if len(self.clients) > 0:
                message = input(f'Server ({self.user}) > ')
                self.broadcast(message, f'Server ({self.user}) said:', None)

    def two_way(self, conn, user):
        while True:
            message = self.recv_full(conn)
            self.broadcast(message, user, conn)

        conn.close()
        print(f'[+] Client disconnected from {addr[0]}:{addr[1]}')
        self.clients.remove(conn)

    def recv_full(self, conn):
        raw_message_len = self.recvall(conn, 4)
        if not raw_message_len:
            return None
        message_len = unpack('>I', raw_message_len)[0]
        # Read the message data
        return self.recvall(conn, message_len).decode('utf-8')

    @staticmethod
    def recvall(conn, n):
        data = bytearray()
        while len(data) < n:
            packet = conn.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
    
    @staticmethod
    def send_full(conn, data):
        data = data.encode('utf-8')
        conn.sendall(pack('>I', len(data)) + data)
        return True

    def broadcast(self, message, user, conn):
        for client in self.clients:
            if client != conn:
                self.send_full(client, f'{user} said:\n{message}')


# main function
def main():
    parser = ArgumentParser(description=f'PYIM Server {VERSION}',
                            formatter_class=ArgumentDefaultsHelpFormatter,
                            epilog='''Example Usage:
                            python3 server.py -p 5555 -t''')
    parser.add_argument('-H', '--host', default='0.0.0.0', help='Hostname or IP address to bind to, leave blank to bind to all interfaces')
    parser.add_argument('-p', '--port', default=9999, type=int, help='Port to bind to')
    parser.add_argument('-t', '--two-way', action='store_true', help='Enable two-way communication between the clients, otherwise one-way will only allow the server to send messages to the clients')
    args = parser.parse_args()

    server = Server(args.host, args.port, args.two_way)
    server.start()


if __name__ == '__main__':
    main()
    exit(0)