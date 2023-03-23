import socket
import pickle
import urllib.request
import time

# define server address and port
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 20139

# create socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# bind socket to address and port
server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
flag = True
# perform 3-way handshake
while flag:
    # receive the  packet
    data, client_address = server_socket.recvfrom(1024)
    syn_client_packet = pickle.loads(data)
    print("The rudp server get request")
    # check for the SYN flag
    if '[SYN]' in syn_client_packet["packet code"]:
        array = str(syn_client_packet["packet code"]).split(',')
        type_of_file = array[1]

        # define the url from the request
        if type_of_file == "cat":
            url = 'https://upload.wikimedia.org/wikipedia/commons/a/a5/Red_Kitten_01.jpg'
        elif type_of_file == "dog":
            url = 'https://upload.wikimedia.org/wikipedia/commons/9/94/My_dog.jpg'
        elif type_of_file == "video":
            url = 'https://www.youtube.com/watch?v=4rhpbCcSXVs'
        elif type_of_file == "amit":
            url = 'https://scontent.fsdv2-1.fna.fbcdn.net/v/t39.30808-6/337403624_625560219387248_6776912049187129348_n.jpg?stp=cp6_dst-jpg_s1080x2048&_nc_cat=106&ccb=1-7&_nc_sid=730e14&_nc_ohc=pKIbnxA08i8AX-dg44t&_nc_ht=scontent.fsdv2-1.fna&oh=00_AfCtWnMUP7cZ4mPd6zAMADKlygwiLdxUrWUSTySxqDp7xg&oe=64210FC4'
        else:
            url = 'http://www.amitdvir.com/'

        print("got SYN ack")
        # create SYN-ACK packet
        syn_packet = pickle.dumps({"image_data": None, "serial number": -1, "packet code": '[SYN, ACK]'})
        # send the SYN-ACK packet
        server_socket.sendto(syn_packet, client_address)
        try:
            # Set the timeout to 1 second
            server_socket.settimeout(3)
            # Receive ACK packet
            data, client_address = server_socket.recvfrom(1024)  # change from 1024
            syn_client_packet = pickle.loads(data)
            # check for the ACK flag
            if '[ACK]' in syn_client_packet["packet code"]:
                print("got SYN-ACK")
                flag = False
        except TimeoutError:
            flag = False

with urllib.request.urlopen(url) as f:
    chunk_list = []
    indicator_dic = {}
    index = 0
    while True:
        # Read data from file
        chunk = f.read(960)
        chunk_list.append(chunk)
        indicator_dic.update({index: chunk})
        index += 1
        if len(chunk) < 960:
            break
    serial_num = 0
    # Create dic of need to send chunk
    cwnd_dic = {}
    dupack_dic = {"serial number": -1, "counter": 0}

    # congestion control variables
    cwnd = 1  # congestion window
    ssthresh = 64  # slow start threshold
    congestion_avoidance = False

    # cubic variables
    w_max = 256
    K = 0.4
    beta = 0.7
    C = 0.4
    T = 0
    last_time = time.time()

    # Set the socket to non-blocking mode
    server_socket.setblocking(False)

    # Send data from chunk_list:
    while len(indicator_dic) > 0:

        if not congestion_avoidance:
            # slow start:
            if cwnd < ssthresh:  # if the window smaller then the ssthresh
                cwnd += 1
            # linear:
            else:
                cwnd += 1 / cwnd
        else:  # congestion avoidance:

            # Calculate the scaling factor K based on the current window size and elapsed time since the last window reduction
            elapsed_time = time.time() - last_time
            K = ((w_max * (1 - beta)) / C) ** (1 / 3)
            T = elapsed_time
            # Calculate the new congestion window size using the cubic function
            curr_cwnd = (C * (T - K) ** 3 + w_max)

            if curr_cwnd >= cwnd:
                cwnd = curr_cwnd
            else:
                w_max = cwnd
                ssthresh = max(cwnd / 2, 1)
                cwnd = ssthresh
                last_time = time.time
                congestion_avoidance = False  # back to slow start
        try:
            if len(cwnd_dic) < cwnd:  # add chunks to list
                for key in indicator_dic:
                    if len(cwnd_dic) < cwnd:
                        cwnd_dic.update({key: indicator_dic[key]})
                    else:
                        break
            else:  # remove chunks from the list
                for key in cwnd_dic:
                    if len(cwnd_dic) > cwnd:
                        cwnd_dic.pop(key)
                    else:
                        break
        except RuntimeError:
            continue

        # If congestion window is not full, send a new packet
        if len(cwnd_dic) > 0:
            for key in cwnd_dic:
                data = pickle.dumps({"image_data": chunk_list[key], "serial number": key, "packet code": "PUSH"})
                # Send data to client
                server_socket.sendto(data, client_address)

                # Record the time of sending this packet
                send_time = time.time()

            # Receive ACK packet from client
        try:
            # Set the timeout to 1 second
            server_socket.settimeout(1)
            try:
                # Receive ACK packet
                data, client_address = server_socket.recvfrom(8192)  # change from 1024
            except ConnectionResetError:
                continue
            if data is not None:
                ack_packet = pickle.loads(data)
                if ack_packet["last serial number"] in indicator_dic:
                    # remove from indicator_dic
                    indicator_dic.pop(ack_packet["last serial number"])

                if ack_packet["last serial number"] in cwnd_dic:
                    # remove from cwnd_dic
                    cwnd_dic.pop(ack_packet["last serial number"])
                # check for 3 duplicate ACKs
                if ack_packet["last serial number"] == dupack_dic["serial number"]:
                    dupack_dic["counter"] += 1
                    # Perform congestion control based on the number of duplicate ACKs
                    if dupack_dic["counter"] >= 3:
                        ssthresh = max(cwnd / 2, 1)
                        cwnd = ssthresh
                        dupack_dic["counter"] = 0
                else:
                    dupack_dic["serial number"] = ack_packet["last serial number"]
                    dupack_dic["counter"] = 1

        except socket.timeout:
            # Timeout occurred, retransmit the first unacknowledged packet
            for key in cwnd_dic:
                data = pickle.dumps({"image_data": chunk_list[key], "serial number": key,
                                     "packet code": "RESEND"})
                server_socket.sendto(data, client_address)

                # Perform congestion control
                ssthresh = 1
                cwnd = ssthresh
                send_time = time.time()
                break

    # send exit packet to the client 10 times to ensure he got it.
    for i in range(10):
        data = pickle.dumps({"image_data": chunk_list[0], "serial number": -1, "packet code": "EXIT"})
        # Send data to client
        server_socket.sendto(data, client_address)

    # receive the rest ack's
    flag = True
    while flag:
        try:
            data, client_address = server_socket.recvfrom(1024)
            ack_packet = pickle.loads(data)
            if ack_packet["packet code"] == "EXIT":
                flag = False
                print("The server gets the last ack")
        except TimeoutError:
            continue
        except socket.timeout:
            continue
        except pickle.UnpicklingError:
            continue

    # Set the socket to blocking mode
    server_socket.setblocking(True)
    print("set blocking mode -> True")

    try:
        # Set the timeout to 1 second
        server_socket.settimeout(1)
        # receive the FIN packet
        data, client_address = server_socket.recvfrom(1024)
        fin_packet = pickle.loads(data)

        # check for the FIN-ACK flag
        if '[FIN, ACK]' in fin_packet["packet code"]:
            print("gets the FIN packet from client")
            # create ACK packet with a random sequence number
            ack_packet = pickle.dumps({"image_data": None, "serial number": -1, "packet code": '[ACK]'})

            # send the ACK packet
            server_socket.sendto(ack_packet, client_address)

            # create FIN packet with a random sequence number
            fin_packet = pickle.dumps({"image_data": None, "serial number": -1, "packet code": '[FIN, ACK]'})
            # send the FIN packet
            server_socket.sendto(fin_packet, client_address)

            # receive the FIN packet
            data, client_address = server_socket.recvfrom(1024)
            fin_ack_packet = pickle.dumps(data)

            if '[ACK]' in fin_ack_packet["packet code"]:
                print("Close the connection")
    except socket.timeout:
        pass

# close the socket
server_socket.close()
print("File sent successfully.")
