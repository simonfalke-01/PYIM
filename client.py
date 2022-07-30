import PYIM
import argparse
from textwrap import dedent


def parse_args():
    parser = argparse.ArgumentParser(description='PYIM server', epilog=dedent('''Example usage:
    python3 client.py -H 192.168.1.123 -p 5555
    python3 client.py -p 5555'''))
    parser.add_argument('-H', '--host', type=str, default='localhost', help='Hostname or IP address to connect to')
    parser.add_argument('-p', '--port', type=int, default=9999, help='Port to connect to')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    client = PYIM.Client(args.host, args.port)
    client.connect_to_server()


if __name__ == '__main__':
    main()