import socket
from threading import Thread
from random import randint

peer_ip = socket.gethostbyname(socket.gethostname())
peer_port = randint(2001, 3000)

tracker_port = 2000

id = 0
contact_list = {}

print(f"IP: {peer_ip} PORT: {peer_port}")

tracker_ip = input("Digite o endereço ip do super nó: ")
connect_to = (tracker_ip, tracker_port)

svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
svr.bind((peer_ip, peer_port))
svr.listen(5)

clt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clt.connect((tracker_ip, tracker_port))
clt.send(f"ID;{peer_ip};{peer_port}".encode("utf-8"))

def check():
    return True

def server():
    global id
    global connect_to
    global clt


    while True:
        con, adr = svr.accept()

        while True:
            data = con.recv(1024)
            commands = data.decode("utf-8")

            for command in commands.split("X"):
                if command == "":
                    continue

                print(f"Comando recebido por p{id}: {command}") 

                data1, data2, data3 = command.split(";")

                if (data1 == "ID") and (id == 0):
                    id = data3
                    print(f"MEU NOVO ID: {id}")

                elif data1 != f"P{id}":
                    clt.sendto(f"{command}X".encode("utf-8"), connect_to) # envia a mensagem codificada em bits

                elif data1 == f"P{id}":
                    if data2 == "CONNECT_WITH":
                        clt.close()
                        
                        connect_to = (data3[2:16], int(data3[19:23]))
                        print(connect_to)
                        clt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        clt.connect(connect_to)

                    if data2 == "NEW_ID":
                        id = data3
                        data3 = int(data3) + 1
                        clt.sendto(f"{data1};{data2};{data3}X".encode("utf-8"), connect_to)
                    if data2 == "CHECK_CONTACT":
                        result = check(data3)

                        if result == False:
                            clt.sendto(data, connect_to)

Thread(target=server).start()
