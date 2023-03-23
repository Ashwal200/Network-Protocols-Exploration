import io
import socket
import time

from PIL import Image
import requests
import os
import pickle

CHUNK_SIZE = 1024
SERVER_ADDRESS = 'localhost'

print("Choose the protocol that you want:\n -> rudp\n -> tcp")
protocol_type = input("Enter the protocol that you want: ")
print("Choose from the following options which files do tou want:\n -> cat\n -> dog\n -> html\n -> video\n -> amit")
type_of_file = input("Enter the file that you want: ")
# Make a GET request to Server 1
response = requests.get("http://localhost:30701/"+type_of_file+"/"+protocol_type)

# Extract the URL for Server 2 from the response headers
url = response.headers["127.0.0.1"]

def open_file(response_file):
    if type_of_file == "html":
        print("The type of the file is "+ type_of_file)
        with open(type_of_file, "w") as f:
            f.write(response_file.text)

    elif type_of_file == "video":
        print("The type of the file is "+ type_of_file)
        with open(type_of_file+".mp4", "wb") as f:
            f.write(response_file.content)

    else:
        # Save the image to a file
        with open(type_of_file+".jpg", "wb") as f:
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
    client_socket.settimeout(15)

    # perform 3-way handshake
    flag = True
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
                {"packet code": "ACK", "last serial number": data["serial number"]})
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
    client_socket.close()
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
