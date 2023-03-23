import socket

# DNS server address and port
DNS_ADDRESS = '127.0.0.1'
DNS_PORT = 53

# Domain name to look up
domain = input("Enter a domain name:")

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Construct the DNS query packet
query = b''
query += b'\xab\xcd' # Query ID
query += b'\x01\x00' # Flags
query += b'\x00\x01' # Questions
query += b'\x00\x00' # Answer RRs
query += b'\x00\x00' # Authority RRs
query += b'\x00\x00' # Additional RRs
for label in domain.split('.'):
    query += bytes([len(label)]) + label.encode('utf-8')
query += b'\x00' # End of domain name
query += b'\x00\x01' # Query type: A (IPv4 address)
query += b'\x00\x01' # Query class: IN (Internet)

# Send the DNS query packet to the server
sock.sendto(query, (DNS_ADDRESS, DNS_PORT))
print(f'Sent DNS query to {DNS_ADDRESS}:{DNS_PORT}')

# Receive the DNS response packet from the server
response, address = sock.recvfrom(1024)
print(f'Received DNS response from {address[0]}:{address[1]}')

# Parse the DNS response packet
ip_address = socket.inet_ntoa(response[-4:])
print('IP address:', ip_address)