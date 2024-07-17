# DNS, DHCP, and HTTP Protocols Project

## Overview

This project explores the fundamental networking protocols that enable the internet to function seamlessly: Domain Name System (DNS), Dynamic Host Configuration Protocol (DHCP), and Hypertext Transfer Protocol (HTTP). Additionally, we delve into the role of Redirect Servers in network communications.


## Introduction

### DNS

A Domain Name System (DNS) is a decentralized and hierarchical naming system that identifies computers accessible via the internet or other Internet Protocol (IP) networks. It translates human-friendly domain names into numerical IP addresses required by computers to locate devices and services using underlying network protocols. Essentially, DNS serves as the internet’s "phonebook," allowing users to connect to websites using domain names instead of IP addresses.

### DHCP

Dynamic Host Configuration Protocol (DHCP) is a client/server protocol that automatically provides an Internet Protocol (IP) host with its IP address and other related configuration information, such as the subnet mask and default gateway. Defined by RFCs 2131 and 2132, DHCP allows hosts to obtain required TCP/IP configuration information from a DHCP server.

### HTTP

Hypertext Transfer Protocol (HTTP) is a protocol for fetching resources such as HTML documents. It forms the foundation of data exchange on the Web and operates on a client-server model, where requests are initiated by clients (usually web browsers) and responses are provided by servers. HTTP is an application layer protocol built on top of TCP (transport layer) and IP (network layer).

### Redirect Servers

Redirect Servers are used to direct requests to the appropriate IP addresses. When a request is made to a Redirect server, it returns the IP address of the desired user agent. This mechanism is commonly used in Voice over IP (VoIP) communications.

## How It Works

### DNS Operation

Every internet-connected device has a unique IP address. DNS servers convert human-friendly domain names (e.g., www.example.com) into computer-friendly IP addresses, enabling browsers to load internet resources without users needing to memorize IP addresses.

### DHCP Operation

A DHCP server stores configuration information in a database, including valid IP addresses and other TCP/IP configuration parameters for all clients on the network. When a DHCP-enabled client accepts a lease offer, it receives a valid IP address, DHCP options (e.g., default gateway, DNS servers), and a lease duration.

### HTTP Operation

HTTP operates as an application layer protocol on top of TCP. Clients (web browsers) send requests, and servers respond with the requested resources. HTTP is extensible and can fetch not only hypertext documents but also images, videos, and other media. It can also be used to post content to servers.

### Redirect Operation

When using a Redirect server, a request is made to the server, which returns the IP address of the user agent being contacted. The user agent then directly communicates with the intended recipient. If the invitation is accepted, communication continues using the Real-time Transport Protocol (RTP).

## Benefits

### DNS Benefits

- Simplifies the user experience by allowing the use of domain names instead of IP addresses.
- Decentralized and scalable.

### DHCP Benefits

- Minimizes configuration errors.
- Reduces network administration efforts.
- Ensures reliable IP address configuration.

### HTTP Benefits

- Facilitates the exchange of web resources.
- Extensible to support various types of media.
- Foundation of web communications.

### Redirect Benefits

- Efficiently directs network traffic.
- Used in various applications, including VoIP.

## Conclusion

This project provides an in-depth understanding of DNS, DHCP, and HTTP protocols, and the role of Redirect Servers in network communications. By exploring these fundamental technologies, we gain insights into the mechanisms that enable seamless internet connectivity and resource exchange.

## How to Run

### Running DNS Server and Client

1. Run the DNS server:
    ```sh
    sudo python3 DNS.py
    ```
2. Run the DNS client:
    ```sh
    sudo python3 DNS_Client.py
    ```
3. Enter the URL that you want.

### Running DHCP Server and Client

1. Run the DHCP server:
    ```sh
    sudo python3 DHCP.py
    ```
2. Run the DHCP client:
    ```sh
    sudo python3 DHCP_Client.py
    ```

### Running Application Without Packet Loss

1. Kill all the ports that may be in use:
    ```sh
    sudo kill -9 `sudo lsof -t -i:53`
    sudo kill -9 `sudo lsof -t -i:20139`
    sudo kill -9 `sudo lsof -t -i:30701`
    sudo kill -9 `sudo lsof -t -i:8000`
    ```
2. Run the application:
    ```sh
    sudo python3 application.py
    ```
3. Enter the URL that you want.
4. Enter the protocol that you want.
5. Enter the file that you want.

### Running Application With Packet Loss

1. Kill all the ports that may be in use:
    ```sh
    sudo kill -9 `sudo lsof -t -i:53`
    sudo kill -9 `sudo lsof -t -i:20139`
    sudo kill -9 `sudo lsof -t -i:30701`
    sudo kill -9 `sudo lsof -t -i:8000`
    ```
2. Run the DHCP and DNS combined server:
    ```sh
    sudo python3 dhcp_dns.py
    ```
3. Enter the URL that you want.
4. Introduce packet loss:
    ```sh
    sudo tc qdisc add dev lo root netem loss 10%
    ```
5. Run the application:
    ```sh
    sudo python3 app.py
    ```
6. Enter the protocol that you want.
7. Enter the file that you want.
