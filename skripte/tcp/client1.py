import sys
import socket
import selectors
import types

import klase_v3 as nrm

def process_information_from_server(recv_data):
    # Pretpostavka je da server salje informacije o peer-u.
    # Te su informacije formatirane ovako: '127.0.0.1:1111'
    global peer

    # Razdvajam ip adresu od porta iz dobivene poruke
    inbound_server_data = recv_data.decode('utf-8').split(':')
    
    peer.address = (inbound_server_data[0], int(inbound_server_data[1]))

    print('Primljene informacije o peeru:\n name={}, address={}'.format( peer.name, peer.address ) )

    
def process_information_from_peer(recv_data):
    # Dobio sam podatke od peer-a.
    # Zasad samo printam te podatke (jer su podaci samo ugodan pozdrav)
    print('Received msg from peer: {}'.format(recv_data.decode("utf-8")))

def listen_for_peer_requests():

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind( client.address )
    
    sock.listen()
    sock.setblocking(False)
    
    print('listening on {}'.format(client.address))

    # selectors.EVENT_READ jer ovaj socket samo slusa zahtjeve. Kad primi zahtjev stvori
    # novi socket koji cita i pise!
    sel.register(sock, selectors.EVENT_READ, data=None)
    
def accept_received_peer_requests(sock):

    conn, addr = sock.accept()
    print("Accepted connection from", addr)

    conn.setblocking(False)

    # connID moze biti 1 ili 2. 
    # 1 znaci da socket komunicira sa STUN serverom, a 2 da socket komunicira sa peer-om.
    connID = 2

    data = types.SimpleNamespace(
        connID=connID,
        outb=messageForPeer,
    )

    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    
    sel.register(conn, events, data=data)

def start_connection_with_peer():
    # Connect to Peer

    connID = 2
    print('Connecting to peer ({})'.format(connID))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind( client.address )

    sock.setblocking( False )
    sock.connect_ex( peer.address )

    data = types.SimpleNamespace(
        connID=connID,
        outb=messageForPeer,
    )

    events = selectors.EVENT_READ | selectors.EVENT_WRITE

    sel.register(sock, events, data=data)

def start_connection_with_server():
    # Connect to Server

    connID = 1
    print('Connecting to server ({})'.format(connID))
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind( client.address )

    sock.setblocking( False )
    sock.connect_ex( server.address )

    data = types.SimpleNamespace(
        connID=connID,
        outb=request,
    )

    events = selectors.EVENT_READ | selectors.EVENT_WRITE

    sel.register(sock, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print('Primljeno {} sa {}'.format(recv_data, data.connID)
            # U ovom sam trenutku sa servera primio informacije o peer-u
            # Primljene informacije je potrebno procesuirati i spremiti peer-ovu
            # adresu u neku varijablu!
            
            # connID moze biti 1 ili 2. 1 znaci da se radi o vezi sa serverom. 2 znaci da se radi o
            # vezi sa peer-om.
            if data.connID == 1:
                # Smatra se da ce server poslati informacije koje trazim o peer-u.
                process_information_from_server(recv_data)
                # Ukoliko se to dogodi, peer.address ce imati neku vrijednost pa mogu probati
                # uspostaviti izravnu vezu s peer-om.
                if peer.address != None:
                    start_connection_with_peer()

            if data.connID == 2:
                process_information_from_peer(recv_data)
                
        else:
            print("closing connection", data.connID)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print("sending", repr(data.outb), "to connection", data.connID)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

## Main

sel = selectors.DefaultSelector()

client = None
peer = None

# Procitaj vlastiti username te peer-ov username!
if len(sys.argv) == 3:
    client = nrm.Host( sys.argv[1] )
    peer = nrm.Host( sys.argv[2] )

else:
    print('Neispravan broj argumenata!')
    exit()

if client == None or peer == None:
    print('Nepoznata korisnicka imena!')
    exit()

server = nrm.Host( 'STUN', ('192.168.3.10', 8888) )
client.address = ('192.168.1.10', 8890)

request = str.encode( '{}->{}'.format(client.name, peer.name) )
messageForPeer = str.encode( 'Hey {}'.format( peer.name ) )


listen_for_peer_requests()
start_connection_with_server()

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                # Key.data je None samo kad se primi zahtjev za uspostavu veze od peer-a!
                if key.data is None:
                    accept_received_peer_requests(key.fileobj)
                else:
                    service_connection(key, mask)
                
        if not sel.get_map():
            break
except KeyboardInterrupt:
        print( "Gasim...")
finally:
    sel.close()
