import socket
import sys
import selectors
import types

import klase_v3 as nrm

def processConnectionRequest(clientName, peerName):

    peer = None

    if clientName in Clients and peerName in Clients:
        peer = nrm.Host( peerName, Clients[peerName] )
    else:
        return None
        
    messageForClient = str.encode('{}:{}'.format( peer.address[0], peer.address[1] ) )
    print('messageForClient: {}'.format( messageForClient ) )
    
    Requests.pop( clientName, None)
    return messageForClient

def process_received_data(data, address):
    
    inbound_client_data = data.decode('utf-8').split('->')
    
    # inbound_client_data[0] je ime klijenta.
    client = nrm.Host( inbound_client_data[0], address )
    
    if client.name not in Clients:
        Clients[client.name] = client.address

    if client.name not in Requests:
        # inbound_client_data[1] je ime peer-a.
        Requests[client.name] = inbound_client_data[1]

    return client.name
    
def accept_wrapper(sock):
    # Prihvati zahtjev za komunikacijom sa klijentom te stvori novi socket preko kojeg ce se ta komunikacija
    # odvijati. Varijabla conn sadrzi novostvoreni socket, addr je adresa klijenta
    conn, addr = sock.accept()
    print("Accepted connection from", addr)

    conn.setblocking(False)
    
    # Varijabla data nam sluzi za povezivanje nekih podataka sa nasim socketom conn.
    # Ta ce nam varijabla posluziti kako bi se moglo pratiti stanje u kojem se socket conn nalazi.
    # Primjerice, tek nakon stvaranja socketa conn, zadajemo informaciju data.addr koja pamti s kojom IP adresom
    # komuniciramo.
    # Data.usr pamti ime korisnika na toj IP adresi.
    # Data.outb pamti poruku koju saljemo preko socketa conn na adresu data.addr.
    # Data.isServed = False nam govori da klijentu na adresi data.addr nismo dostavili informacije
    # o peer-u koje je od nas trazio.
    data = types.SimpleNamespace(addr=addr, usr=b"", outb=b"", isServed=False)
    
    # Varijabla events odreduje za koju vrstu komunikacije ce se socket conn koristiti.
    # selectors.EVENT_READ znaci da ce socket samo slusati primljene poruke, a na njih nece odgovarati
    # selectors.EVENT_WRITE znaci da ce socket samo slati poruke, a odgovore na te poruke nece slusati
    # selectors.EVENT_READ | selectors.EVENT_WRITE znaci da ce socket slusati i slati poruke.
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    
    # Nakon ispravnog postavljanja socketa, registriraj ga pomocu selector.register()
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    
    # Prilikom svakog ulaza u ovu funkciju, neka se izvrši provjera
    # unutar Requests koja provjerava je li informacija koju
    # client sa ovog socketa zahtjeva postala dostupna!
    # Ukoliko je, neka se pošalje ta informacija nazad ka klijentu!
    sock = key.fileobj
    data = key.data
    
    # Varijabla mask sadrzi neku kombinaciju vrijednosti selectors.EVENT_READ i selectors.EVENT_WRITE.
    # Ta nam informacija govori kakav tip komunikacije ce se izvoditi preko ovog socket-a.
    # Hoce li socket samo primati poruke, ili ce ih i slati, ili neka druga kombinacija.
    
    # Ukoliko se radi o socketu koji zeli primati poruke, izvrsiti ce se ovaj dio koda
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print('Primljen zahtjev za komunikacijom sa {}'.format(data.addr))
            data.usr = process_received_data(recv_data, data.addr)
        else:
            print('Gasim komunikaciju sa {}'.format(data.addr))
            sel.unregister(sock)
            sock.close()

    # Ukoliko se radi o socketu koji zeli slati poruke, izvrsiti ce se ovaj dio koda
    if mask & selectors.EVENT_WRITE:
        
        # Ukoliko socket vec ima zadano sto ce slati, neka to posalje
        if data.outb:
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]
            
        # Ima li server potrebne informacije za odgovor na zahtjev klijenta?
        if not data.isServed:
            if (data.usr != None) and ( data.usr in list(Requests.keys()) ):
                messageForClient = processConnectionRequest( data.usr, Requests[data.usr] )
                if messageForClient != None:
                    # Ako ima potrebne informacije, stavi ih na red za slanje
                    # Oznaci socket kao uspjesno obraden 
                    data.outb = messageForClient
                    data.isServed = True

sel = selectors.DefaultSelector()

Clients = {}
Requests = {}

server = nrm.Host( 'STUN', ('192.168.3.10', 8888) )

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind( server.address )
tcp_socket.listen()
tcp_socket.setblocking( False )

sel.register( tcp_socket, selectors.EVENT_READ, data=None )

print('Server slusa...')

try:
    while True:

        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                # Prihvati komunikaciju sa klijentom te izradi novi socket preko kojega ce se novostvorena
                # komunikacija odvijati!
                accept_wrapper( key.fileobj )
            else:
                # Servisiraj zahtjeve klijenata
                service_connection( key, mask )
                
except KeyboardInterrupt:
        print( "Gasim...")
finally:
    tcp_socket.close()
    sel.close()
