import sys
import pyroomba
from getopt import getopt
from socket import *


opts, args = getopt(sys.argv[1:], 'i:p:d:', ['interface=', 'port=', 'device='])

interface = ''
port = 7420
device = 0

for o, a in opts:
    if o in ('-i', '--interface'):
        interface = a
    elif o in ('-p', '--port'):
        port = int(a)
    elif o in ('-d', '--device'):
        device = a

roomba = pyroomba.RoombaClassic(device)
roomba.start()
roomba.safe()
roomba.leds(255, 255)

sock = socket()
sock.bind((interface, port))
sock.listen(1)

monitors = []

def handle_command(client, command):
    """Handles a user command"""
    global quit, motors
    parts = command.split(' ')
    name = parts[0]
    args = parts[1:]
    if name == 'sensor':
        if args[0] in roomba.latest:
            response = "%s: %s\n" % (args[0], roomba.latest[args[0]])
    elif name == 'monitor':
        for sensor in args:
            monitors.append(sensor)
    elif name == 'unmonitor':
        for sensor in args:
            monitors.remove(sensor)
    elif name == 'stop':
        motors = [ 0, 0 ]
    elif name == 'quit':
        quit = True
        raise Exception('Quit')
    else:
        if hasattr(roomba, name):
            method = getattr(roomba, name)
            intargs = [ int(a) for a in args ] # Try all integers, most args are!
            method(*intargs)

buf = ''
def receive_command(client):
    """Receives and handles a command from the client if one has been received"""
    global buf
    try:
        buf += client.recv(1024)
    except error, e:
        code, message = e
        if code == 35:
            return # No data waiting, that's fine
        raise e # Some other error. Crash!
    commands = buf.split("\n")
    buf = commands[-1] # Yank off last element which is an incomplete command
    commands = commands[:-1] # Strip down to complete commands
    for command in commands:
        handle_command(client, command)

quit = False

while not quit:
    motors = [0, 0]
    client, client_address = sock.accept()
    print "Client connected", client_address
    client.setblocking(False)
    
    def idle():
        """Idle function for handle a command"""
        receive_command(client)
        
        for sensor in monitors:
            response = "%s: %s\n" % (sensor, roomba.latest[sensor])
            client.send(response)
    
    try:
        roomba.run(idle_func = idle)
    except Exception, e:
        print e
        roomba.stop()
        client.close()
        client = None

