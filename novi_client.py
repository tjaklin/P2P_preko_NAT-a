import socket
import sys
import time


# Serverova adresa je staticna
serverAddressPort   = ("192.168.3.10", 8888)
bufferSize          = 128

peerAddressPort     = ()

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Prepare message
msgFromClient = "userA+192.168.1.10:8888+userB"
bytesToSend = str.encode(msgFromClient)

UDPClientSocket.sendto(bytesToSend, serverAddressPort)

# Set a timer!
startTime = ''

## Listen for incoming datagrams
while(True):
    
    if not all(peerAddressPort):
        #print('Tuple peerAddressPort empty...')
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)
        msg = msgFromServer[0].decode("utf-8")
    
        # Format poruke= '192.168.x.y:cvbn'
        msgFormatted = msg.split(":")
        if len(msgFormatted) == 2:
            peerAddressPort = (msgFormatted[0], int(msgFormatted[1]))
            print('Peer Info Received: {}'.format(peerAddressPort))
        else:
            print('S:', msg)
        
    else:
        # Salji Peeru poruku svakih 2.5 sekundi!
        if not startTime:
            startTime = time.time()
            print('Timer started!')
        if time.time() - startTime > 2.5:
            startTime = time.time()
            UDPClientSocket.sendto(str.encode('Poyy UserB!'), peerAddressPort)
        # Sad mi fali samo jos implementacija slusanja poruka od Peera!!!!

UDPClientSocket.close()
