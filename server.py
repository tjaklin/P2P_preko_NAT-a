import socket
## POTREBNO DODATI:

#1) Prilikom primitka nove poruke od nekog klijenta potrebno je prvo zapisati informacije o tom klijentu
#   u oba dictionary-ja. Nakon toga prolazi se kroz sve parove u dictionary-ju activeRequestDictionary te se
#   pokusava obraditi svaki par.
#   Parovi se obraduju na nacin da se provjeri jesu li informacije o oba korisnika iz nekog para dostupne
#   u activeUsersAddressDictionary! Ukoliko jesu, potrebno je poslati informacije korisniku ključu!




localIP     = "192.168.3.10"
localPort   = 8888
bufferSize  = 128

## Init a dict for holding active computers' public+private IP and ports
# dict structure =>  'username' : [privateIP_Port, publicIP_Port]
activeUsersAddressDictionary=	{
    'userS' : ['192.168.4.10:8888', '192.168.4.10:8888' ]
}

## Ovo je dict primljenih, a neobradenih, zahtjeva za uspostavljanje komunikacije
activeRequestDictionary= {
	'userX' : 'userY'
}

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind( (localIP, localPort) )
print("UDP server up and listening...\n")
msgFromServer = 'bad data'

# Listen for incoming datagrams
while(True):

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

    message = bytesAddressPair[0].decode("utf-8").split("+")
    clientUsername = message[0]
    clientPrivateIP = message[1]
    clientPeerUsername =  message[2]
    
    clientPublicIP = "{}:{}".format(bytesAddressPair[1][0], bytesAddressPair[1][1])
    
    print("C: [", clientUsername, '->', clientPrivateIP, ',', clientPublicIP, ']', 'requesting communication with ', clientPeerUsername)
    
    # Always add current client to dictionary
    userExistsFlag = False
    for k in activeUsersAddressDictionary.keys():
        if k == clientUsername:
            activeUsersAddressDictionary[clientUsername] = [clientPrivateIP, clientPublicIP]
            print('{} already exists'.format(clientUsername))
            userExistsFlag = True
    if userExistsFlag == False:
        activeUsersAddressDictionary.setdefault(clientUsername, [])
        activeUsersAddressDictionary[clientUsername].append(clientPrivateIP)
        activeUsersAddressDictionary[clientUsername].append(clientPublicIP)
        print('Adding {} to dict'.format(clientUsername))

    # Proccess client's peer communication request
    # Dodaj zahtjev u dict!
    userExistsFlag = False
    for k in activeRequestDictionary.keys():
        if k == clientUsername:
            userExistsFlag = True
            break
    if userExistsFlag == False:
        activeRequestDictionary[clientUsername] = clientPeerUsername

    userExistsFlag = False
    for k in activeUsersAddressDictionary.keys():
        if k == activeRequestDictionary[clientUsername]:
            resultingAddressPort = activeUsersAddressDictionary[clientPeerUsername][1]
            msgFromServer = 'Requested peer {} exists!\n{}\'s Address= {}'.format(clientPeerUsername, clientPeerUsername, resultingAddressPort)
            activeRequestDictionary.pop(clientUsername, None)
            userExistsFlag = True
            break
    if userExistsFlag == False:
        msgFromServer = 'Requested peer {} is non-existing!'.format(clientPeerUsername)

    # Sending a reply to client
    bytesToSend = str.encode(msgFromServer)
    UDPServerSocket.sendto(bytesToSend, bytesAddressPair[1])



























