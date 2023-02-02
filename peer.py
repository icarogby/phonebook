import socket
from threading import Thread
import os

host = socket.gethostbyname(socket.gethostname())
port = 2000
port2 = 2001
id = None

peer_list = []
contact_list = {}

print(f"HOST: {host} PORT: {port}")

tracker = input("Digite o endereço ip do super nó: ")
connect_to = tracker

# cliente
peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET = IPV4 | SOCK_STREAM = TCP
peer.connect((tracker, port)) # conecta ao servidor
peer.sendto(f"ID,{host}, aa".encode("utf-8"), (tracker, port)) # envia a mensagem codificada em bits


# servidor
peer2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET = IPV4 | SOCK_STREAM = TCP
peer2.bind((host, port2)) # bind = vincular
peer2.listen(4) # limites de conexões

def conec():
    global peer2

    con, adr = peer2.accept()

def check(contact):
    global contact_list

    if contact in contact_list:
        return contact_list[contact]
    else:
        return False

def recive():
    global id

    
    
    while True:
        data = peer.recv(1024) # 1024 = tamanho do buffer
        decoded_data = data.decode("utf-8")
        print(decoded_data) 

        data1, data2, data3 = decoded_data.split(",")
        print("debug")
        
        if data1 == "ID":
            id = data3
            print(f"meu id é : {id}")
            print(f"minha porta é: {port2}")

        elif data1 != id:
            peer.sendto(data, connect_to) # envia a mensagem codificada em bits

        elif data1 == id:
            if data2 == "CONNECT_WITH":
                peer.close()
                peer.connect((data3, port))
                connect_to = data3

            if data2 == "NEW_ID":
                id = data3
                data3 = str(int(data3) + 1)
                peer.sendto(f"{data1},{data2},{data3}", connect_to)
            if data2 == "CHECK_CONTACT":
                result = check(data3)

                if result == False:
                    peer.sendto(data, connect_to)
                
                print("oi")

def send():
    while True:
        comando = input("\nDigite a mensagem: \n")

        if comando == "exit":
            peer.sendto(f"TK,REMOVE_FROM_LIST,{id}".encode("utf-8"), (connect_to, port))
            peer.close()
            break
        else:
            msg = f"TK,DEBUG,aaaaaaadebugg{id}"
            peer.sendto(comando.encode("utf-8"), (connect_to, port))

Thread(target=send).start()
Thread(target=recive).start()
Thread(target=conec).start()
print("test")

