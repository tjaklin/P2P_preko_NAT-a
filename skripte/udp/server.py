import socket
import klase as nrm

### FUNKCIJE

def proccessConnectionRequest(clientName, peerName):

    client = None
    peer = None

    if peerName in Clients and clientName in Clients:
        peer = nrm.Host( peerName, Clients[peerName] )
        client = nrm.Host( clientName, Clients[clientName] )
        
        messageForClient = str.encode('{}:{}'.format( peer.address[0], peer.address[1] ) )
        
        messageForPeer = str.encode('{}:{}'.format( client.address[0], client.address[1] ) )
        
        udp_socket.sendto(messageForClient, client.address)
        udp_socket.sendto(messageForPeer, peer.address)
        
        Requests.pop(clientName, None)
        Requests.pop(peerName, None)
        print('Information sent.')
        
    else:
        print('[WARNING] Cannot resolve {}\'s communication request for {}'.format(clientName, peerName))

### GLAVNI DIO

# Sprema informacije o svim klijentima s kojima stupa u kontakt.
# Ime klijenta je key, a tuple koji sadrzi adresu i port broj je value.
Clients = {}

# Sprema informacije o svim zahtjevima koje mu klijenti salju.
# Ime klijenta je key, a ime peer-a je value.
Requests = {}

server = nrm.Host( 'STUN', ('192.168.3.10', 8888) )

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.bind( server.address )

print('Server slusa...')

while(True):

    (data, address) = udp_socket.recvfrom( 128 )
    
    # Format poruke je ovakav: 'userA->userB'.
    # userA je ime klijenta, a userB je ime peer-a.
    # Kako server nikad prije nije sreo klijenta 'userA', njegove ce informacije
    # spremiti u Clients.
    # inbound_client_data sadrzi klijentov zahtjev za uspostavu komunikacije sa peer-om.
    # STUN server ce spremiti taj zahtjev u dictionary Requests.
    inbound_client_data = data.decode('utf-8').split('->')

    # inbound_client_data[0] je ime klijenta.
    client = nrm.Host( inbound_client_data[0], address )
    
    if client.name not in Clients:
        Clients[client.name] = client.address

    if client.name not in Requests:
        # inbound_client_data[1] je ime peer-a.
        Requests[client.name] = inbound_client_data[1]
        
    #for k in Clients.keys():
        #print('{} : {}'.format(k, Clients[k]))
    #for k in Requests.keys():
        #print('{} : {}'.format(k, Requests[k]))
    
    print('Primljene informacije o klijentu:\n name={}, address={}'.format( client.name, client.address ))
        
    # Sad treba proci kroz Requests i procesuirati svaki zahtjev!
    print('Procesuiranje zahtjeva...')
    
    for k in list(Requests.keys()):
        if k in Requests:
            proccessConnectionRequest(k, Requests[k])
