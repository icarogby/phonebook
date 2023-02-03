import socket
from threading import Thread

# arrumer porta aleatoria

connect_to = None

host = socket.gethostbyname(socket.gethostname())
port = 2000

peers_list = [(socket.gethostbyname(socket.gethostname()), 2000)]

print(f"HOST: {host} PORT: {port}")

# Socket cliente
clt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Socket servidor
svr = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
svr.bind((host, port))
svr.listen(5)

def server():
    global peers_list
    global connect_to

    while True:
        con, adr = svr.accept()

        while True:
            print(peers_list)

            #recebe a mensagem do ultimo par da rede ou de novo par
            data = con.recv(1024)
            commands = data.decode("utf-8")
            
            for command in commands.split("X"):
                if command == "":
                    continue

                print(f"Comando recebido pelo traker: {command}")

                # data1 = ID | data2 = comando | data3 = informação personalizada
                data1, data2, data3, = command.split(";")

                # novo par entra na rede
                if(data1 == "ID"):
                    peers_list.append((adr[0], int(data3)))

                    if(len(peers_list) == 2):
                        connect_to = peers_list[1]
                        clt.connect(connect_to)
                        clt.send(f"ID;NEW_ID;{len(peers_list) - 1}X".encode("utf-8"))
                    
                    # se não for o unico par da rede, vai ser o novo ultimo par
                    if(len(peers_list) > 2):
                        old_final_peer_number = len(peers_list) - 2

                        # envia a mensagem para a rede
                        # antigo ultimo par, conecte-se com o novo ultimo par
                        clt.send(f"P{old_final_peer_number};CONNECT_WITH;{peers_list[-1]}X".encode("utf-8"))

                        # novo ultimo par, esse é seu id
                        clt.send(f"ID;NEW_ID;{len(peers_list) - 1}X".encode("utf-8"))
                        
                        break
          
                elif(data1[0] == "P"):
                    clt.send(command.encode("utf-8"))
                
                elif(data1 == "TK"):
                    # TK, REMOVE_FROM_LIST, NUMERO DO PEER QUE SAIU
                    if(data2 == "REMOVE_FROM_LIST"):
                        if data3 == str(len(peers_list) - 1):
                            del peers_list[-1]
                            clt.send(f"P{len(peers_list) - 1};CONNECT_WITH;{peers_list[0]}X".encode("utf-8"))
                        elif data3 != "1":
                            #numero do peer que saiu
                            quit_number = int(data3)
                            del peers_list[quit_number]
                            before_number = quit_number - 1
                            after_ip = peers_list[quit_number + 1]

                            clt.send(f"P{before_number};CONNECT_WITH;{after_ip}X".encode("utf-8"))
                            clt.send(f"P{quit_number + 1};NEW_ID;{quit_number}X".encode("utf-8"))
                        if data3 == "1":
                            del peers_list[1]
                            clt.send(f"P2;NEW_ID;{1}X", peers_list[1])
                    elif(data2 == "DEBUG"):
                        print(f"{data3}")

for i in range(4):
    Thread(target=server).start()
