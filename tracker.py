import socket
from threading import Thread

localHost = socket.gethostbyname(socket.gethostname())
localPort = 2000

peers_list = [(socket.gethostbyname(socket.gethostname()), 2000)]

print(f"HOST: {localHost} PORT: {localPort}")

tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tracker.bind((localHost, localPort))
tracker.listen(3) # primeiro conectado, ultimo conectado, novo conectado

def connection():
    while True:
        con, adr = tracker.accept()
        print(adr)

        while True:
            print(peers_list)
            #recebe a mensagem do ultimo par da rede ou de novo par
            data = con.recv(1024)

            if not data:
                break

            decoded_data = data.decode("utf-8")
            print(decoded_data)

            # data1 = ID | data2 = comando | data3 = informação personalizada
            data1, data2, data3, = decoded_data.split(",")

            # novo par entra na rede
            if(data1 == "ID"):
                peers_list.append(adr)
                con.sendto(f"ID, NEW_ID, {len(peers_list) - 1}".encode("utf-8"), peers_list[1])
                
                # se não for o unico par da rede, vai ser o novo ultimo par
                if(len(peers_list) > 2):
                    final_peer_number = len(peers_list) - 1
                    old_final_peer_number = len(peers_list) - 2

                    # envia a mensagem para a rede
                    # antigo ultimo par, conecte-se com o novo ultimo par
                    con.sendto(f"P{old_final_peer_number},CONNECT_WITH,{peers_list[-1]}".encode("utf-8"), peers_list[1])
                    # novo ultimo par, esse é seu id
                    con.sendto(f"P{final_peer_number}, NEW_ID, {len(peers_list) - 1}".encode("utf-8"), peers_list[1])

            
            elif(data1[0] == "P"):
                con.sendto(data, peers_list[1])
            
            elif(data1 == "TK"):
                # TK, REMOVE_FROM_LIST, NUMERO DO PEER QUE SAIU
                if(data2 == "REMOVE_FROM_LIST"):
                    if data3 == str(len(peers_list) - 1):
                        del peers_list[-1]
                        con.sendto(f"P{len(peers_list) - 1},CONNECT_WITH,{peers_list[0]}", peers_list[1])
                    elif data3 != "1":
                        #numero do peer que saiu
                        quit_number = int(data3)
                        del peers_list[quit_number]
                        before_number = quit_number - 1
                        after_ip = peers_list[quit_number + 1]

                        con.sendto(f"P{before_number},CONNECT_WITH, {after_ip}", peers_list[0])
                        con.sendto(f"P{quit_number + 1},NEW_ID,{quit_number}", peers_list[0])
                    if data3 == "1":
                        del peers_list[1]
                        con.sendto(f"P2,NEW_ID,{1}", peers_list[1])
                elif(data2 == "DEBUG"):
                    print(f"{data3}")

for i in range(3):
    Thread(target=connection).start()
