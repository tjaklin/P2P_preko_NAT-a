import socket

### FUNKCIJE  
def printPeerData(clientName):
    if clientName in KnownClients:
        print('[{}-> {}, {}]'.format(clientName, KnownClients[clientName][0], KnownClients[clientName][1]))
    else:
        print('[NOTICE] No client {} in KnownClients!'.format(clientName))
  
#def serveConnectionRequest(clientName):
    #if clientName in KnownConnectionRequests:
        #peerName = KnownConnectionRequests[clientName]
        #if peerName in KnownClients:
            #print('Serving connection request: {}->{}'.format(clientName, peerName))
            #return KnownClients[peerName][1]
        #else:
            #print('No peer {} in KnownClients!'.format(peerName))
            #return ''
    #else:
        #print('No client {} in KnownConnectionRequests!'.format(clientName))
        #return ''

def getPeerAddress(peerName):
    if peerName in KnownClients:
        return KnownClients[peerName][1]
    else:
        print('[WARNING] getPeerAddress({}) -> No such Peer!'.format(peerName))
        return ''

def proccessConnectionRequest(clientName, peerName):
    #if clientName in KnownConnectionRequests:
    peerAddressPort = getPeerAddress(peerName)
    if not peerAddressPort:
        print('[WARNING] Cannot resolve {}\'s communication request for {}'.format(clientName, peerName))
    else:
        clientAddressPort = getPeerAddress(clientName)
        
        # Notify Client of Peer's Address information
        dataForClient = str.encode('{}:{}'.format(peerAddressPort[0], peerAddressPort[1]))
        # Notify Peer of Client's Address information
        dataForPeer = str.encode('{}:{}'.format(clientAddressPort[0], clientAddressPort[1]))
        
        
        UDPServerSocket.sendto(dataForClient, clientAddressPort)
        print('[NOTICE] Sending {}\'s Address to {}!'.format(peerName, clientName))
        
        UDPServerSocket.sendto(dataForPeer, peerAddressPort)
        print('[NOTICE] Sending {}\'s Address to {}!'.format(clientName, peerName))
        
        KnownConnectionRequests.pop(clientName, None)
        KnownConnectionRequests.pop(peerName, None)


### GLAVNI DIO

## Network layer properties
localIP     = "192.168.3.10"
localPort   = 8888

bufferSize  = 128

## Init Dicts
# Known Clients
KnownClients=	{
    'userS' : [ ('192.168.4.10', 8888), ('192.168.4.10', 8888) ]
}
# Known Connection Requests
KnownConnectionRequests= {
	
}

## Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind( (localIP, localPort) )
print("[NOTICE] UDP server up and listening...\n")
msgFromServer = 'bad data'

## Listen for incoming datagrams
while(True):

    clientAddressPort = UDPServerSocket.recvfrom(bufferSize)
    
    # Primjer poruke= userA+192.168.1.10:8888+userB
    clientMessage = clientAddressPort[0].decode("utf-8").split("+")
    clientUsername = clientMessage[0]
    clientPeerUsername =  clientMessage[2]

    clientPrivateIP = clientMessage[1].split(":")
    clientPrivateIP = ( clientPrivateIP[0], int(clientPrivateIP[1]) )

    clientPublicIP = clientAddressPort[1]
    
    # Add Client's data to KnownClients and KnownConnectionRequests Dicts
    KnownClients.setdefault(clientUsername, [])
    KnownClients[clientUsername].append(clientPrivateIP)
    KnownClients[clientUsername].append(clientPublicIP)
    KnownConnectionRequests[clientUsername] = clientPeerUsername
    print('[NOTICE] Adding {} to Dicts...'.format(clientUsername))

    # Print Client's data
    printPeerData(clientUsername)
    print('[NOTICE] Received a communication request for {}!'.format(clientPeerUsername))
    
    # Try to proccess Client's Communication Request
    ###### OVAJ ZAKOMENTIRANI DIO ISPOD SE PRESKACE JER SE IONAK VRTI NAKON!! #######
    #if clientUsername in KnownConnectionRequests:
        #peerAddressPort = serveConnectionRequest(clientUsername)
        #if not peerAddressPort:
            #print('Cannot resolve {}\'s communication request for {}'.format(clientUsername, clientPeerUsername))
        #else:
            #Notify Client of Peer's Address information
            #bytesToSend = str.encode(peerAddressPort)
            #UDPServerSocket.sendto(bytesToSend, clientAddressPort[1])
            #print('Sending Peer\'s Address to Client!')
        #proccessConnectionRequest(clientUsername, clientPeerUsername)
        
    # Sad trebam proci kroz KnownConnectionRequests i procesuirati svaki slucaj!
    print('[NOTICE] Trying to proccess requests in KnownConnectionRequests...')
    for k in list(KnownConnectionRequests.keys()):
        if k in KnownConnectionRequests:
            proccessConnectionRequest(k, KnownConnectionRequests[k])
































