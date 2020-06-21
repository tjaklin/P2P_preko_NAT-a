import socket
import sys
import klase as nrm

### MAIN

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

udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
udp_socket.setblocking(0)

# Zatrazi od STUN servera informacije o peer-ovoj adresi
request = str.encode( '{}->{}'.format(client.name, peer.name) )
udp_socket.sendto(request, server.address)

isOver = False
startTime = ''

while(isOver == False):
    try:
        # Ukoliko jos ne znam peer-ovu adresu zakljucujem da ce svaka poruka koju socket primi
        # dolaziti sa STUN servera.
        if peer.address == None:
            (data, address) = udp_socket.recvfrom( 128 )

            # Format poruke je '127.0.0.1:1234'. Potrebno je poruku pretvoriti iz stringa u tuple
            # Stoga se string reze na dva dijela, prvi ce dio biti IP adresa u string formatu, a drugi dio
            # ce biti port broj koji ce se spremiti kao integer
            inbound_server_data = data.decode('utf-8').split(':')
            peer.address = (inbound_server_data[0], int(inbound_server_data[1]))
            
            print('Primljene informacije o peeru:\n name={}, address={}'.format( peer.name, peer.address ) )
            
        # Ukoliko znam peer-ovu adresu, mogu pokusati uspostaviti komunikaciju s njim.
        else:   
                # Prvo saljem jedan paket ka peer-u
                messageForPeer = str.encode( 'Hey {}'.format( peer.name ) )
                udp_socket.sendto( messageForPeer, peer.address )
                                
                # Zatim provjeravam je li mi peer takoder poslao paket
                ( data, addr ) = udp_socket.recvfrom( 128 )

                print('Primljena poruka:\n {}'.format( data.decode('utf-8') ) )

    except socket.error:
        # Ako nisu primljeni podaci zove se ova iznimka koja se ignorira
        pass
    
    except KeyboardInterrupt:
        print( "Gasim...")
        break

udp_socket.close()
