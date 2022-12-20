# importing required modules
import os
import socket
import threading
from time import sleep
from datetime import datetime

HOST = '192.168.43.190'
PORT = 17034

MAX_NUM_CLIENTS = 10
ACTIVE_CLIENTS = []
####################################################
def hand_shake(client):
    while(True):
        username = client.recv(2048).decode('utf-8')

        if username != '':
            ACTIVE_CLIENTS.append((username, client))
            prompt_msg = "{username} is inside!"
            send_msg_to_all(prompt_msg)
            break 
        else:
            print("Username is empty!")
    listen = threading.Thread(target=listen_for_messages, args=(client, username, ))
    listen.start()
####################################################
def send_msg(client, message):
    client.sendall(message.encode('utf-8'))
####################################################
def send_image(client, filename):
    count = 0
    
    uzunluk = os.path.getsize(filename)

    with open(filename, 'rb') as file:

        for _ in range(int(uzunluk)):
            if count < int(uzunluk):
                image_data =file.read(2048)
                client.sendall(image_data)
                count += 2048
####################################################
def send_msg_to_all(message):
    for client in ACTIVE_CLIENTS:
        send_msg(client[1], message)    
####################################################
def send_image_to_all(filename):
    for client in ACTIVE_CLIENTS:
        send_image(client[1],filename)
####################################################
def listen_for_messages(client, username):
    while(True):
        message = client.recv(2048).decode('utf-8')
        if message != '' and message == 'TEXT':
            text_message = client.recv(2048).decode('utf-8')
            msg = f"{username}: {text_message}" + "\n"
            send_msg_to_all('TEXT')
            sleep(0.2)
            send_msg_to_all(msg)
        if message != '' and message == 'IMAGE':
            sleep(0.2)
            size = client.recv(2048).decode('utf-8')
            sleep(0.2)
            total = 0
            file_name = f'{str(datetime.now().time())}.jpg'
            with open(file_name, "wb") as file:
                for _ in range(int(size)):
                    if total < int(size):
                        image_chunk = client.recv(2048)
                        file.write(image_chunk)
                        total += 2048

            send_msg_to_all('IMAGE')
            sleep(0.2)
            send_msg_to_all(username)
            sleep(0.2)
            send_msg_to_all(str(os.path.getsize(file_name)))
            sleep(0.2)
            send_image_to_all(file_name)
       
####################################################
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((HOST, PORT))
        print(f"Server is running on port {PORT}")
    except Exception:
        print(f'Unable to bind to Host {HOST} on Port {PORT}.\
        Make sure on other application is running on port {PORT}')

    server.listen(MAX_NUM_CLIENTS)
    while(True):
        client_soc, client_addr = server.accept()
        print(f"Successfully connected to client {client_addr[0]} {client_addr[1]}")
        threading.Thread(target=hand_shake, args=(client_soc, )).start()
        

# driver function
if __name__ == '__main__':
    main()

