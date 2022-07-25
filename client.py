from socket import socket, AF_INET, SOCK_STREAM
from getpass import getuser
from threading import Thread
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from sys import exit, stdout
from struct import pack, unpack

VERSION = 'v0.0.1'


# client that connects to server.py
class Client:
    def __init__(self, host, port):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.host = host
        self.port = port
        self.user = getuser()
        self.conn_type = 'Two-Way Connection'

    def connect(self):
        self.client.connect((self.host, self.port))
        self.send_full(self.client, self.user)
        self.conn_type = self.recv_full(self.client)

        print(f'[+] Connected to {self.host}:{self.port}.')
        print(f'[+] Connection type: {self.conn_type}')

        if self.conn_type == 'One-Way Connection':
            self.one_way()
        elif self.conn_type == 'Two-Way Connection':
            self.two_way()
        
        self.client.close()

    def one_way(self):
        while True:
            message = self.recv_full(self.client)
            print(f'[+] {message}')
    
    def two_way(self):
        output_thread = Thread(target=self.one_way)
        input_thread = Thread(target=self.send_thread)
        output_thread.start()
        input_thread.start()
        output_thread.join()
        input_thread.join()

    def receive_thread(self):
        while True:
            message = self.recv_full(self.client)
            print(f'[+] {message}')

    def send_thread(self):
        while True:
            message = input(f'{self.user} > ')
            self.send_full(self.client, message)

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


# main function
def main():
    parser = ArgumentParser(description=f'PYIM Client {VERSION}',
                            formatter_class=ArgumentDefaultsHelpFormatter,
                            epilog='''Example usage:
                            python3 client.py -H localhost -p 5555''')
    parser.add_argument('-H', '--host', type=str, default='localhost', help='Hostname or IP address of server')
    parser.add_argument('-p', '--port', type=int, default=9999, help='Port of server')
    args = parser.parse_args()

    client = Client(args.host, args.port)
    client.connect()


if __name__ == '__main__':
    main()
    exit(0)