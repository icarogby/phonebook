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

def peer():
    global id
    global connect_to
    global clt
    global contact_list

    while True:
        con, adr = svr.accept()

        while True:
            data = con.recv(1024)
            commands = data.decode("utf-8")

            if not data:
                break

            for command in commands.split("X"):
                if command == "":
                    continue

                print(f"Comando recebido por p{id}: {command}") 

                data1, data2, data3 = command.split(";")

                if (data1 == "ID"):
                    if id == 0:
                        id = data3
                        print(f"MEU NOVO ID: {id}")
                    else:
                        clt.send(f"{command}X".encode("utf-8"))

                elif data1[0] == f"P":
                    if data1 != f"P{id}":
                        clt.send(f"{command}X".encode("utf-8"))

                    elif data1 == f"P{id}":
                        if data2 == "CONNECT_WITH":
                            clt.close()
                            
                            connect_to = (data3[2:16], int(data3[19:23]))
                            print(connect_to)
                            clt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            clt.connect(connect_to)
                            print("Conectado com o novo par")

                        if data2 == "NEW_ID":
                            id = int(data3)
                            data3 = id + 1
                            clt.send(f"P{int(data1[1])+1};{data2};{data3}X".encode("utf-8"))
                        
                        if data2 == "FINDED":
                            print(f"Contato encontrado: {data3}")
                
                elif data1 == "SC":
                        if data3 in contact_list:
                            clt.send(f"{data2};FINDED;{contact_list[data3]}".encode("utf-8"))
                            print(f"Achado aqui: {contact_list[data3]}")
                        else:
                            if data2 == f"P{id}":
                                print("Contato não encontrado")
                            else:
                                clt.send(f"{command}X".encode("utf-8"))
                elif data1 == "TK":
                    clt.send(f"{command}X".encode("utf-8"))
                        

def user_commands():
    global clt

    while True:
        print("\nLISTA TELEFONICA")
        print("1 - Adicionar contato")
        print("2 - Listar contatos")
        print("3 - Buscar contato")
        print("4 - Meu ID")
        print("5 - Meus pares")
        print("6 - Sair da rede")
        
        command = int(input("\nDigite o comando: "))

        if command == 1:
            name = input("Nome: ")
            number = input("Número: ")

            contact_list[name] = number
            print("\nContato salvo")
        
        if command == 2:
            print(contact_list)
        
        if command == 3:
            name = input("Nome: ")
            
            if name in contact_list:
                print(contact_list[name])
            else:
                clt.send(f"SC;P{id};{name}".encode("utf-8"))
        if command == 4:
            print(id)
        
        if command == 5:
            print(connect_to)
        if command == 6:
            clt.send(f"TK;REMOVE_FROM_LIST;P{id}".encode("utf-8"))
            clt.close()
            svr.close()
            print("program closed")


Thread(target=peer).start()
Thread(target=user_commands).start()
