import socket
import sys


# Serverova adresa je staticna
serverAddressPort   = ("192.168.3.10", 8888)
bufferSize          = 128

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Prepare message
msgFromClient = "userA+192.168.1.10:8888+userB"
bytesToSend = str.encode(msgFromClient)

UDPClientSocket.sendto(bytesToSend, serverAddressPort)

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

msg = msgFromServer[0].decode("utf-8")

print("S:", msg)

# Ok sad cekam jos poruku od Peer-a...
msgFromPeer = UDPClientSocket.recvfrom(bufferSize)
print('aaaaa')

peerPublicIP = "{}:{}".format(msgFromPeer[1][0], msgFromPeer[1][1])
print(peerPublicIP)

msg = msgFromPeer[0].decode("utf-8")
print("Peer:", msg)

UDPClientSocket.close()
