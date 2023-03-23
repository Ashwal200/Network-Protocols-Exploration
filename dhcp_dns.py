from scapy.all import *
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
import subprocess


################# ----------> DHCP <------------ ##################
# Spawn a new process for file1 and continue executing file2
subprocess.Popen(['python3', 'DHCP.py'])
time.sleep(1)

mac_address = get_if_hwaddr(conf.iface)
ip_address = None


def offer_packet(packet):
    print("Receiving DHCP offer")
    send_request_packet(packet)


def ack_packet(packet):
    print("Receiving DHCP ack")


def send_discover_packet():
    # First the DHCP Discover message is the first message sent by the client throughout the network
    # (that is, for all users of this method of sending they call Broadcast)
    # and this is so that the DHCP server knows that the client wants to connect to the network

    # Build the DHCP discover
    # * Ether - Ethernet source and destination addresses
    # * IP - This sets the IP source and destination addresses
    # * UDP - This sets the UDP source and destination ports
    # * BOOTP - This sets the BOOTP fields in the packet
    # * DHCP - This sets the DHCP options in the packet

    ether = Ether(src=mac_address, dst='ff:ff:ff:ff:ff:ff')
    ip_layer = IP(src='0.0.0.0', dst='255.255.255.255')
    udp = UDP(sport=68, dport=67)
    bootp = BOOTP(op=1, chaddr=mac_address)
    dhcp = DHCP(options=[('message-type', 'discover'), 'end', 'pad'])
    discover = ether / ip_layer / udp / bootp / dhcp
    print("sending DHCP Broadcast...")
    # The sendp function in Scapy is used to send a packet
    # * The discover parameter is the packet that is being sent
    # * The verbose=False argument is used to suppress any output
    sendp(discover, verbose=False)

    # This line of code sets up a packet sniffer using Scapy's sniff function
    sniff(prn=offer_packet, filter='(port 67 or port 68)', count=1)


def send_request_packet(offer):
    # 3. The DHCP Request message is the third message in the communication that the client sends as a response to
    # the Offer message and it is sent to tell the DHCP server that the client accepts the offer and is ready to
    # receive more information about the network.
    global ip_address
    ip_address = offer[BOOTP].yiaddr
    print(ip_address)

    # Build the DHCP request
    # * Ether - Ethernet source and destination addresses
    # * IP - This sets the IP source and destination addresses
    # * UDP - This sets the UDP source and destination ports
    # * BOOTP - This sets the BOOTP fields in the packet
    # * DHCP - This sets the DHCP options in the packet

    ether = Ether(src=mac_address, dst='ff:ff:ff:ff:ff:ff')
    ip_layer = IP(src='0.0.0.0', dst='255.255.255.255')
    udp = UDP(sport=68, dport=67)
    bootp = BOOTP(op=1, chaddr=mac_address, yiaddr=ip_address, siaddr=get_if_addr(conf.iface))
    dhcp = DHCP(options=[('message-type', 'request'),
                         ('requested_addr', ip_address),
                         ('server_id', offer[DHCP].options[1][1]), 'end', 'pad'])
    request = ether / ip_layer / udp / bootp / dhcp
    print("sending DHCP Request...")
    # The sendp function in Scapy is used to send a packet
    # * The request parameter is the packet that is being sent
    # * The verbose=False argument is used to suppress any output
    sendp(request, verbose=False)

    sniff(prn=ack_packet, filter='(port 67 or port 68)', count=1)


def send_release_packet():
    print("Sending DHCP release")
    global ip_address
    # Build the DHCP release
    # * Ether - Ethernet source and destination addresses
    # * IP - This sets the IP source and destination addresses
    # * UDP - This sets the UDP source and destination ports
    # * BOOTP - This sets the BOOTP fields in the packet
    # * DHCP - This sets the DHCP options in the packet
    ether = Ether(src=mac_address, dst='ff:ff:ff:ff:ff:ff')
    ip_layer = IP(src=ip_address, dst='255.255.255.255')
    udp = UDP(sport=68, dport=67)
    bootp = BOOTP(op=1, chaddr=mac_address, yiaddr=ip_address)
    dhcp = DHCP(options=[('message-type', 'release'), 'end', 'pad'])

    release = ether / ip_layer / udp / bootp / dhcp
    print("sending DHCP Release")
    # The sendp function in Scapy is used to send a packet
    # * The release parameter is the packet that is being sent
    # * The verbose=False argument is used to suppress any output
    sendp(release, verbose=False)


# Send a DHCP discover packet to start the DHCP process
send_discover_packet()

################# ----------> DNS <------------ ##################


# DNS server address and port
DNS_ADDRESS = '127.0.0.1'
DNS_PORT = 53

# Domain name to look up
domain = input("Enter a domain name:")

subprocess.Popen(['python3', 'DNS.py'])
time.sleep(2)
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Construct the DNS query packet
query = b''
query += b'\xab\xcd'  # Query ID
query += b'\x01\x00'  # Flags
query += b'\x00\x01'  # Questions
query += b'\x00\x00'  # Answer RRs
query += b'\x00\x00'  # Authority RRs
query += b'\x00\x00'  # Additional RRs
for label in domain.split('.'):
    query += bytes([len(label)]) + label.encode('utf-8')
query += b'\x00'  # End of domain name
query += b'\x00\x01'  # Query type: A (IPv4 address)
query += b'\x00\x01'  # Query class: IN (Internet)

# Send the DNS query packet to the server
sock.sendto(query, (DNS_ADDRESS, DNS_PORT))
print('Sent DNS query to {}:{}'.format(DNS_ADDRESS, DNS_PORT))

# Receive the DNS response packet from the server
response, address = sock.recvfrom(1024)
print('Received DNS response from {}:{}'.format(address[0], address[1]))

# Parse the DNS response packet
ip_address_from_dns = socket.inet_ntoa(response[-4:])
print('IP address:', ip_address_from_dns)

if domain != "www.application.com":
    exit(1)

################# ----------> APP <------------ ##################


import io
import socket
import time

from PIL import Image
import requests
import os
import pickle

CHUNK_SIZE = 1024
SERVER_ADDRESS = ip_address_from_dns
print("Choose the protocol that you want:\n -> rudp\n -> tcp")
protocol_type = input("Enter the protocol that you want: ")
print("Choose from the following options which files do tou want:\n -> cat\n -> dog\n -> html\n -> video\n -> amit")
type_of_file = input("Enter the file that you want: ")



# Make a GET request to Server 1
response = requests.get("http://localhost:30701/" + type_of_file + "/" + protocol_type)
print(response.headers)
# Extract the URL for Server 2 from the response headers
url = response.headers["127.0.0.1"]


def open_file(response_file):
    print(response_file.__class__)
    if type_of_file == "html":
        print("The type of the file is " + type_of_file)
        with open(type_of_file, "w") as f:
            f.write(response_file.text)

    elif type_of_file == "video":
        print("The type of the file is " + type_of_file)
        with open(type_of_file + ".mp4", "wb") as f:
            f.write(response_file.content)

    else:
        with open(type_of_file + ".jpg", "wb") as f:
            print("The type of the file is " + type_of_file + " image")
            f.write(response_file.content)
            img = Image.open(io.BytesIO(response_file.content))
            img.show()


response_file = b''
time.sleep(5)

if protocol_type == "tcp":
    # Make a GET request to Server 2 to retrieve the image
    response_file = requests.get(url)
    print("tcp")
    open_file(response_file)
else:
    recieve = url.split(':')
    recieve_port = recieve[2].split('/')
    print(recieve_port[0])
    port = recieve_port[0]
    print("rudp")

    # create socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # set timeout for receiving data
    client_socket.settimeout(15)  # Changed from 1 !

    flag = True
    # perform 3-way handshake

    while flag:
        syn_packet = pickle.dumps({"image_data": None, "serial number": -1, "packet code": '[SYN],' + type_of_file})
        client_socket.sendto(syn_packet, (SERVER_ADDRESS, int(port)))
        print("sent SYN ack")
        # receive SYN-ACK packet
        try:
            # Set the timeout to 1 second
            client_socket.settimeout(3)
            data, server_address = client_socket.recvfrom(1024)
            syn_ack_packet = pickle.loads(data)
            # check for SYN-ACK flag
            if '[SYN, ACK]' in syn_ack_packet["packet code"]:
                ack_packet = pickle.dumps({"image_data": None, "serial number": -1, "packet code": '[ACK]'})
                # send ACK packet
                client_socket.sendto(ack_packet, server_address)
                print("sent ACK ack")
                flag = False
        except TimeoutError:
            continue
        except socket.timeout:
            continue

    # Set the socket to non-blocking mode
    client_socket.setblocking(False)

    chunk_list = {}
    while True:
        try:
            # read data from server
            data_bytes, server_address = client_socket.recvfrom(4096)  # change
            data = pickle.loads(data_bytes)

            # if all data received, break the loop
            if data["packet code"] == "EXIT":
                break

            # add received data to file
            chunk_list.update({data["serial number"]: data["image_data"]})

            # create packet with serial number and
            packet = pickle.dumps(
                {"packet code":"ACK", "last serial number": data["serial number"]})
            # send the packet to server
            client_socket.sendto(packet, server_address)
        except socket.timeout:
            continue
        except BlockingIOError:
            continue

    # send exit packet to the server to let him know that this is the last of the chunck's ack
    # create packet with EXIT massage
    packet = pickle.dumps(
        {"packet code": "EXIT", "last serial number": 0})
    # send the packet to server
    client_socket.sendto(packet, server_address)

    # Set the socket to blocking mode
    client_socket.setblocking(True)

    try:

        # create FIN packet
        fin_packet = pickle.dumps({"image_data": None, "serial number": -1, "packet code": '[FIN, ACK]'})

        # send the FIN packet
        client_socket.sendto(fin_packet, server_address)

        # receive the FIN-ACK packet
        data, server_address = client_socket.recvfrom(1024)
        fin_ack_packet = pickle.loads(data)

        # check for the FIN-ACK flag
        if '[ACK]' in fin_ack_packet["packet code"]:

            # receive the FIN packet
            data, server_address = client_socket.recvfrom(1024)
            fin_packet = pickle.dumps(data)

            if '[FIN, ACK]' in fin_packet["packet code"]:
                # create ACK packet with a random sequence number
                ack_packet = pickle.dumps({"image_data": None, "serial number": -1, "packet code": '[FIN, ACK]'})
                # send the ACK packet
                client_socket.sendto(ack_packet, server_address)
    except Exception:
        pass
    # close the socket
    print("open file for writing")
    if type_of_file == "dog" or type_of_file == "cat":

        with open(type_of_file + ".jpg", 'wb') as f:
            for i in range(len(chunk_list)):
                f.write(chunk_list[i])
    elif type_of_file == "html":
        with open(type_of_file + ".txt", 'wb') as f:
            for i in range(len(chunk_list)):
                response_file += chunk_list[i]
            f.write(response_file)
    else:
        with open(type_of_file + ".mp4", 'wb') as f:
            for i in range(len(chunk_list)):
                response_file += chunk_list[i]
            f.write(response_file)
    print('File received successfully.')

################# ----------> DHCP <------------ ##################


# Send a DHCP release packet to release the IP address
send_release_packet()
