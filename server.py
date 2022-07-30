import PYIM
import argparse
from textwrap import dedent

def parse_args():
    parser = argparse.ArgumentParser(description='PYIM server', epilog=dedent('''Example usage:
    python3 server.py -H 192.168.1.123 -p 5555
    python3 server.py -p 5555'''))
    parser.add_argument('-H', '--host', type=str, default='0.0.0.0', help='Hostname or IP address to bind to')
    parser.add_argument('-p', '--port', type=int, default=9999, help='Port to listen for connections on')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    server = PYIM.Server(args.host, args.port)
    server.start_server()


if __name__ == '__main__':
    main()
