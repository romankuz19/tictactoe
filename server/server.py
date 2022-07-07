import socket, threading

SERVER_ADDRESS = ("127.0.0.1", 11000)

error_code = '54a0e8c17ebb21a11f8a25b8042786ef7efe52441e6cc87e92c67e0c4c0c6e78' #Код ошибки
acknowledge_code = 'f9236d9e87b6235ec4f2d7e00d60f5a68670c6dcf70f6f2f354a4325f79f1b27' #Код подтверждения

request1 = 'b06aa45eb35423f988e36c022967b4c02bb719b037717df13fa57c0f503d8a20' #Код запроса на получение списка всех свободных игроков

clients = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(SERVER_ADDRESS)

server_socket.listen()
print(f"Server is listening on port {SERVER_ADDRESS[1]}..")

def clientHandler(client_socket, name):
    try:
        while True:
            request = client_socket.recv(1024).decode("utf-8")
            if request == request1:
                data = ""
                for client in clients:
                    if client[1] == False:
                        data = data + client[0] + " "
                client_socket.send(data.encode("utf-8"))
    except:
        delete_index = 0
        for client in clients:
            if client[0] == name:
                delete_index = clients.index(client)

        print(f"Client from IP: {clients[delete_index][2].getsockname()[0]}, PORT: {clients[delete_index][2].getsockname()[1]} disconnected..")

        clients.pop(delete_index)

#Обработка присоединения клиента
while True:
    client_socket, client_address = server_socket.accept()

    #Получаем имя клиента
    name = client_socket.recv(1024).decode("utf-8")

    isExist = False

    for client in clients:
        #Если такое имя уже есть
        if name == client[0]:
            isExist = True
            break
    
    if isExist:
        client_socket.send(error_code.encode("utf-8"))
        continue
    else:
        client_socket.send(acknowledge_code.encode("utf-8"))
            

    #Создаем список характеристик клиента (имя, состояние ожидания, сокет)
    client = []
    client.append(name)
    client.append(False)
    client.append(client_socket)

    #Добавляем список характеристик клиента в список всех клиентов
    clients.append(client)

    #Открываем поток, в котором будем принимать запросы пользователя
    newClientHandler = threading.Thread(target=clientHandler, args=(client_socket,name, ))
    newClientHandler.start()

    print(f"Client has connected from IP: {client_address[0]}, PORT: {client_address[1]}..")
