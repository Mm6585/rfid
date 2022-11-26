import socket
import threading
import time

def start_server():
    print('Start server')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('192.168.43.188', 5000))
    server_socket.listen(2)
    ard_client, track_client = arrange_client(server_socket)

    return ard_client, track_client

def arrange_client(server_socket):
    client_socket1, addr1 = server_socket.accept()
    client_socket2, addr2 = server_socket.accept()

    while(True):
        data1 = client_socket1.recv(32).decode()
        data2 = client_socket2.recv(32).decode()

        if ((data1 == 'arduino') and (data2 == 'track')):
            ard_client = [client_socket1, addr1]
            track_client = [client_socket2, addr2]

            client_socket1.sendall(b'check')
            client_socket2.sendall(b'check')
            
            while(True):
                data1 = client_socket1.recv(32).decode()
                data2 = client_socket2.recv(32).decode()

                if ((data1 == 'check') and (data2 == 'check')):
                    break
            break

        elif ((data2 == 'arduino') and (data1 == 'track')):
            ard_client = [client_socket2, addr2]
            track_client = [client_socket1, addr1]

            client_socket1.sendall(b'check')
            client_socket2.sendall(b'check')

            while(True):
                data1 = client_socket1.recv(32).decode()
                data2 = client_socket2.recv(32).decode()

                if ((data1 == 'check') and (data2 == 'check')):
                    break
            break

    return ard_client, track_client

def server_arduino_TCP(ard_client_socket, ard_addr):
    global id_store, id_history
    
    print('arduino Connected:', ard_addr)

    while (True):
        data = ard_client_socket.recv(32).decode()
        print('arduino signal', data)

        if (data == 'pass1'):
            while(id not in id_store):
                id = input()    # RFID Reader read tag's id
                if (id not in id_history):
                    break

            ard_client_socket.sendall(b'pass reader')
            data = ard_client_socket.recv(32).decode()
            if (data == 'receive id'):
                continue
            elif (data == 'pass1'):
                continue
            time.sleep(0.1)
        elif (data == 'pass2'):
            id_store.append(id)
            id_history.append(id)
            print(str(id), 'pass!')
            continue
        time.sleep(0.5)

def server_track_TCP(track_client_socket, track_addr):
    global id_store
    
    print('track Connected:', track_addr)

    while(True):
        data = track_client_socket.recv(32).decode()
        print('track request:',data)

        if (data == 'request id'):
            while (len(id_store) == 0):
                time.sleep(0.01)
            id = id_store.pop(0)
            while(True):
                track_client_socket.sendall(id.encode())
                data = track_client_socket.recv(32).decode()
                print(data)
                if (data == 'receive id'):
                    break
                time.sleep(0.5)

def run(ard_client, track_client):
    ard_thread = threading.Thread(target=server_arduino_TCP, args=(ard_client[0], ard_client[1]))
    track_thread = threading.Thread(target=server_track_TCP, args=(track_client[0], track_client[1]))
    ard_thread.start()
    track_thread.start()

id_store = list()
id_history = list()

ard_client, track_client = start_server()
run(ard_client, track_client)