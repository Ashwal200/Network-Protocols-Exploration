import socket
import dns.resolver

# set the DNS server address and port
DNS_ADDRESS = '127.0.0.1'
# the DNS port is set to 53, which is the default port used for DNS queries
DNS_PORT = 53

# create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# use the address
sock.bind((DNS_ADDRESS, DNS_PORT))
print(f'DNS server listening on {DNS_ADDRESS}:{DNS_PORT}')

while True:
    # receive DNS query packet from client
    data, address = sock.recvfrom(1024)
    print(f'Received DNS query from {address[0]}:{address[1]}')

    # disassembly a DNS query message to extract the query domain name and query type.
    id = data[:2]
    query = data[12:]
    domain = ''
    i = 0
    while True:
        length = query[i]
        if length == 0:
            break
        i += 1
        domain += query[i:i+length].decode('utf-8') + '.'
        i += length
    query_type = data[-4:-2]

    # Resolve the domain name using dnspython
    resolver = dns.resolver.Resolver()
    print(domain[:-1])
    if domain[:-1] == "www.application.com":
        ip_address = "127.0.0.1"
    else:
        ip_address = str(resolver.resolve(domain[:-1], 'A')[0])

    # Construct the DNS response packet
    response = id
    response += b'\x81\x80' # Flags
    response += b'\x00\x01' # Questions
    response += b'\x00\x01' # Answer RRs
    response += b'\x00\x00' # Authority RRs
    response += b'\x00\x00' # Additional RRs
    response += query
    response += b'\xc0\x0c' # Pointer to domain name
    response += query_type
    response += b'\x00\x01' # Query class: IN (Internet)
    response += b'\x00\x00\x00\x3c' # TTL (60 seconds)
    response += b'\x00\x04' # Data length
    response += socket.inet_aton(ip_address)

    # Send DNS response packet to client
    sock.sendto(response, address)
    print(f'Sent DNS response to {address[0]}:{address[1]}')