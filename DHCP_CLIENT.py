
from scapy.all import *
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether

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
    # Wait for the DHCP process to complete and obtain an IP address
    time.sleep(5)

    # Send a DHCP release packet to release the IP address
    send_release_packet()


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
    ip_layer = IP(src= ip_address, dst='255.255.255.255')
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
