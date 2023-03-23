from scapy.all import *
import time
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether


print("Waiting for incoming request...")
DATA_BASE = ['192.168.0.%d' % i for i in range(100, 200)]
DICTIONARY = {ip: False for ip in DATA_BASE}
COUNT = 0


def increment():
    global COUNT
    COUNT = COUNT + 1

def decrement():
    global COUNT
    COUNT = COUNT - 1


def get_ip():
    global COUNT
    if COUNT == 100:
        print("we already serve 100 IP's...")
        exit(1)
    # Checking for each ip in the dict if he false or true
    for ip in DICTIONARY:
        # If we find ip: false send him
        if DICTIONARY[ip] is False:
            DICTIONARY[ip] = True
            increment()
            return ip
    return None

def create_ip(msg):
    if msg[DHCP] and msg[DHCP].options[0][1] == 1:
        print("DHCP Discover received")
        # Extract the client's MAC address from the message
        ip_src = msg[IP].src

        # Check if the client already has an IP address in our list
        if ip_src in DICTIONARY:
            print("Client already has an IP address assigned:", ip_src)
            return

        # Give the next available IP address to the new client
        ip = get_ip()

        # If we are fully booked, return
        if not ip:
            return

        # 2. The DHCP Offer message is the message with which the DHCP server replies to the
        # Discover message and it contains the IP address that the server offers to the client

        # Build the DHCP offer for the client
        # * Ether - Ethernet source and destination addresses
        # * IP - This sets the IP source and destination addresses
        # * UDP - This sets the UDP source and destination ports
        # * BOOTP - This sets the BOOTP fields in the packet
        # * DHCP - This sets the DHCP options in the packet

        ether = Ether(src=get_if_hwaddr(conf.iface), dst=msg[Ether].src)
        ip_layer = IP(src=get_if_addr(conf.iface), dst='255.255.255.255')
        udp = UDP(sport=67, dport=68)
        bootp = BOOTP(op=2, yiaddr=ip, siaddr=get_if_addr(conf.iface), chaddr=msg[Ether].src)
        dhcp = DHCP(options=[('message-type', 'offer'),('server_id', get_if_addr(conf.iface)),
                            ('lease_time', 60),('subnet_mask', '255.255.255.0'),
                            ('router', get_if_addr(conf.iface)),'end', 'pad'])
        offer = ether / ip_layer / udp / bootp / dhcp
        time.sleep(1)
        print("sending DHCP offer to the client...")
        # The sendp function in Scapy is used to send a packet
        # * The offer parameter is the packet that is being sent
        # * The iface=conf.iface specifies the interface that the packet is being sent out of
        # * The verbose=False argument is used to suppress any output
        sendp(offer, iface=conf.iface, verbose=False)

    elif msg[DHCP] and msg[DHCP].options[0][1] == 3:
        # Extract the client's MAC address and requested IP address from the request
        mac = msg[Ether].src.replace(':', '')
        requested = msg[BOOTP].yiaddr

        # Give the requested IP address to the client
        ip = requested

        # 4. The DHCP Acknowledge message is the last message as part of the D.O.R.A process that
        # the server sends to the client in which additional details about the network are sent.

        # Build the DHCP ACK
        # * Ether - Ethernet source and destination addresses
        # * IP - This sets the IP source and destination addresses
        # * UDP - This sets the UDP source and destination ports
        # * BOOTP - This sets the BOOTP fields in the packet
        # * DHCP - This sets the DHCP options in the packet
        ether = Ether(src=get_if_hwaddr(conf.iface), dst=msg[Ether].src)
        ip_layer = IP(src=get_if_addr(conf.iface), dst='255.255.255.255')
        udp = UDP(sport=67, dport=68)
        bootp = BOOTP(op=5, yiaddr=ip, siaddr=get_if_addr(conf.iface), chaddr=msg[Ether].src)
        dhcp = DHCP(options=[('message-type', 'ack'),('server_id', get_if_addr(conf.iface)),
                            ('lease_time', 1200),('subnet_mask', '255.255.255.0'),
                            ('router', get_if_addr(conf.iface)),('dns', '127.0.0.1'),'end', 'pad'])
        ack = ether / ip_layer / udp / bootp / dhcp
        time.sleep(1)
        print("sending DHCP ack to the client...")
        # The sendp function in Scapy is used to send a packet
        # * The ack parameter is the packet that is being sent
        # * The iface=conf.iface specifies the interface that the packet is being sent out of
        # * The verbose=False argument is used to suppress any output
        sendp(ack, iface=conf.iface, verbose=False)



    elif msg[DHCP] and msg[DHCP].options[0][1] == 7:
        print("DHCP Release received")
        ip = msg[BOOTP].yiaddr
        decrement()
        # Remove the IP address from the list
        if str(ip) in DICTIONARY and DICTIONARY[str(ip)] == True:
            DICTIONARY[str(ip)] = False
            print("IP address {} released".format(ip))


if __name__ == '__main__':
    # This line of code sets up a packet sniffer using Scapy's sniff function
    sniff(filter='udp and (port 67 or port 68)', prn=create_ip)
