import socket
import argparse
from threading import Thread
from struct import pack, unpack
from sys import stdout, stdin, stderr
from getpass import getuser

# version number
VERSION = 'v0.1.0'


def receive_message(conn):
    # message length
    raw_message_length = receive_till_length(conn, 4)
    # no length
    if not raw_message_length:
        return None
    
    message_length = unpack('>I', raw_message_length)[0]
    # return message
    return receive_till_length(conn, message_length).decode('utf-8')

def receive_till_length(conn, n):
    data = bytearray()
    # receive data until length
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    # return bytes
    return data

def send_message(conn, data):
    data = data.encode('utf-8')
    # send 4 bytes message length first then message
    conn.sendall(pack('>I', len(data)) + data)
    return True


class PropagatingThread(Thread):
    def __init__(self, target, callback, *args, **kwargs):
        super().__init__(target=target, args=args, kwargs=kwargs)
        self.callback = callback
        self.__runtime_error = None
        self.__return = None
    
    def run(self):
        try:
            if self._args:
                self.__return = self._target(*self._args)
            else:
                self.__return = self._target()
        except BaseException as e:
            self.__runtime_error = e

        raise socket.error(self.__runtime_error)


class Server:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = host
        self.port = port
        self.clients = {}
        self.user = f'Server ({getuser()})'

    def start_server(self):
        try:
            self.server.bind((self.host, self.port))
            self.server.listen()
            stdout.write(f'[+] Listening on {self.host}:{self.port}.\n')
            self.__handle()
        except socket.error as e:
            stderr.write(f'[!] Bind failed. Error: {e}\n')
            exit(1)

    def __handle(self):
        while True:
            try:
                conn, addr = self.server.accept()
                connected_user = receive_message(conn)

                self.__update_clients(conn, addr, connected_user)

                thread = PropagatingThread(self.__client_handler, self.__disconnect_conn, self.clients[conn])
                stdout.write(f'[+] Client connected from {addr[0]}:{addr[1]} with username {connected_user}.\n')
                try:
                    thread.run()
                except KeyboardInterrupt:
                    stdout.write('[*] Server shutting down...\n')
                    self.__close_server()
                except socket.error as e:
                    stderr.write(f'[!] Client disconnected: {e}\n')
                    self.__disconnect_conn(conn)
                except BaseException as e:
                    stderr.write(f'[!] An error occurred: {e}\n')
                    self.__disconnect_conn(conn)
            except KeyboardInterrupt:
                stdout.write('[*] Server shutting down...\n')
                self.__close_server()
            except socket.error as e:
                stderr.write(f'[!] Socket error: {e}\n')
                exit(1)

    def __client_handler(self, client: list):
        while True:
            message = receive_message(client[0])
            if message is None:
                raise socket.error(client[1])
            self.__broadcast(message, client[0])

    def __update_clients(self, conn, addr, connected_user):
        self.clients.update({conn: [conn, addr, connected_user]})
        return conn

    def __disconnect_conn(self, conn):
        self.clients.pop(conn)
        conn.close()

    def __broadcast(self, message, exclude_conn):
        user = self.clients[exclude_conn][2]

        for client in self.clients:
            if client != exclude_conn:
                send_message(client, self.__generate_message(message, user))
    
    def __generate_message(self, message, user):
        return f'{user}: {message}'
    
    def __close_server(self):
        self.server.close()
        stdout.write('[*] Server closed.\n')
        exit(0)


class Client:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.user = f'{getuser()}'
        self.__ran_receive = None
        self.__ran_send = None

    def connect_to_server(self):
        try:
            self.client.connect((self.host, self.port))
        except socket.error as e:
            stderr.write(f'[!] Connection failed. Error: {e}\n')
            exit(1)
        
        self.__send_message(self.user)

        stdout.write(f'[+] Connected to {self.host}:{self.port}.\n')

        self.ran_receive = PropagatingThread(self.__receive_thread, self.__close_client)
        self.ran_send = PropagatingThread(self.__send_thread, self.__close_client)

        try:
            receive_thread.run()
            send_thread.run()
        except KeyboardInterrupt:
            stdout.write('[*] Client shutting down...\n')
            self.__close_client()
        except socket.error as e:
            stderr.write(f'[!] Client disconnected: {e}\n')
            self.__close_client()

    def __receive_thread(self):
        while True:
            print('Receive thread')
            message = receive_message(self.client)
            if message is None:
                raise socket.error('Empty message')
            stdout.write(f'{message}\n')
    
    def __send_thread(self):
        while True:
            print('Send thread')
            message = self.__ask()
            if message == 'exit':
                self.__close_client()
            else:
                self.__send_message(message)

    def __ask(self):
        stdout.write(f'{self.user} > ')
        return stdin.readline().strip()

    def __send_message(self, message):
        send_message(self.client, message)

    def __receive_message(self):
        return receive_message(self.client)

    def __close_client(self):
        self.client.close()
        stdout.write('[*] Client closed.\n')
        exit(0)