# PYIM - Python Instant Messaging

PYIM, the better CIM.
PYIM is a python script that allows multiple clients to communicate with each other, or broadcasting a message to multiple clients.

## Modes

### Two-way Mode

- Two-way Mode allows clients to communicate with each other
- Server example usage:<br />
`python3 server.py -H 192.168.1.30 -p 5555 -t`<br />
`python3 server.py -p 5555 -t`

### One-way Mode

- One-way Mode allows server to broadcast messages to clients
- Server example usage:<br />
`python3 server.py -H 192.168.1.30 -p 5555`<br />
`python3 server.py -p 5555`

The `-H` flag can be omitted to listen on all interfaces.

### Client Example usage

- `python3 client.py -H 192.168.1.30 -p 5555`<br />
- `python3 client.py -p 5555`

The `-H` flag can be omitted to connect to `localhost`, useful for communication between users on a single host.
