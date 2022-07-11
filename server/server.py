import socket, threading, random, time

SERVER_ADDRESS = ("127.0.0.1", 11000)

error_code = '54a0e8c17ebb21a11f8a25b8042786ef7efe52441e6cc87e92c67e0c4c0c6e78' #Код ошибки
acknowledge_code = 'f9236d9e87b6235ec4f2d7e00d60f5a68670c6dcf70f6f2f354a4325f79f1b27' #Код подтверждения

request1 = 'b06aa45eb35423f988e36c022967b4c02bb719b037717df13fa57c0f503d8a20' #Код запроса на получение списка всех свободных игроков
request2 = '2fc41ef02a3216e4311805a9a11405a41a8d7a9f179526b4f6f2866bff009a10' #Код запроса на отпраку приглашения пользователю
request3 = '3ff16f0155fae419d7c1402dd267a146bba71abaabb5c3d29477aa54729f3472' #Код запроса на отправку ответа на приглашение игроку
request4 = '70337a34b6415ba5fa027f5db805f9393636c6e39de7a76a6ef64398622d2c74' #Код запроса на приостановку потока

response1 = '9e60b7bc9a12f2f193a91b7e41401de9cdf0bdae7f3670cc91634a5b4ceb5e19' #Код ответа на запрос на получение списка свободных игроков
response2 = 'ada2e137475fbfd01168a228fbe0a38a4cee57894ba2ffec5ec9e5c6a5d91156' #Код ответа на запрос на отправку приглашения игроку
response3 = 'c843750529bac77ebc4e2026642fd03c048682b9c98963bb1a938c632b64ab71' #Код ответа на запрос на отправку ответа на приглашение игрока

response4 = '5b828eacedee30f2ea5a6e7fc2e0323ddc6350ab2d7540b08982e3120afb12dd' #Код ответа на получение крестика или нолика
response5 = '838c118150d2f7b40272b6aee2492357b77dfc870209ca9df9cae280e0d5076c' #Код ответа на получение хода противника
response6 = '144a5931ec80d672f104cc4c7e6b978b825ac06df0d7c5774ab7994a35ebcb50' #Код ответа о выигрыше или проигрыше

winCode = '0713d07cd82977b5de4dba918140019fbfecf9883b13ea58f7f2c54f121bb06a' #Код победы
loseCode = 'cc8a30ea6faccd1bd3503e5a9001bbac91871be28a2140be347b2cc9d27d8031' #Код порожения
drawCode = '50f7becde477bb509c7704de62c349247fb3499c03a95e4bce20151cd552dea5' #Код ничьей

clients = []

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(SERVER_ADDRESS)

server_socket.listen()
print(f"Server is listening on port {SERVER_ADDRESS[1]}..")

def checkTurn(game_map, number):
    if game_map[0] == number and game_map[3] == number and game_map[6] == number:
        return True
    if game_map[1] == number and game_map[4] == number and game_map[7] == number:
        return True
    if game_map[2] == number and game_map[5] == number and game_map[8] == number:
        return True
    if game_map[0] == number and game_map[1] == number and game_map[2] == number:
        return True
    if game_map[3] == number and game_map[4] == number and game_map[5] == number:
        return True
    if game_map[6] == number and game_map[7] == number and game_map[8] == number:
        return True
    if game_map[0] == number and game_map[4] == number and game_map[8] == number:
        return True
    if game_map[2] == number and game_map[4] == number and game_map[6] == number:
        return True
    return False

def DrawCheck(game_map):
    for field in game_map:
        if field is None:
            return False
    return True

def gameHandler(index1, index2):
    gameOver = False
    numTurn1 = 0
    numTurn2 = 0

    index1Turn = False
    index2Turn = False

    buttonCode = ''

    game_map = [None] * 9

    #Выдаем крестик или нолик игрокам 
    numSign = random.randint(0, 1)
    time.sleep(0.5)
    numTurn1 = random.randint(0, 1)
    if numTurn1 == 1:
        numTurn2 = 0
    else:
        numTurn2 = 1
    #Если num == 0, тогда игрок с index1 - x, а игрок с index2 - o и наоборот
    if numSign == 0:
        clients[index1][2].send(response4.encode("utf-8"))
        clients[index1][2].send('X'.encode("utf-8"))
        clients[index1][2].send(str(numTurn1).encode("utf-8"))
        clients[index2][2].send(response4.encode("utf-8"))
        clients[index2][2].send('O'.encode("utf-8"))
        clients[index2][2].send(str(numTurn2).encode("utf-8"))
        
        if numTurn1 == 0:
            index2Turn = True
        if numTurn1 == 1:
            index1Turn = True

    if numSign == 1:
        clients[index1][2].send(response4.encode("utf-8"))
        clients[index1][2].send('O'.encode("utf-8"))
        clients[index1][2].send(str(numTurn1).encode("utf-8"))
        clients[index2][2].send(response4.encode("utf-8"))
        clients[index2][2].send('X'.encode("utf-8"))
        clients[index2][2].send(str(numTurn2).encode("utf-8"))

        if numTurn1 == 0:
            index2Turn = True
        if numTurn1 == 1:
            index1Turn = True
        
    while not gameOver:
        #Если ход за первым игроком()
        if index1Turn == True:
            buttonCode = clients[index1][2].recv(1024).decode("utf-8")

            if buttonCode == request1:
                continue

            game_map[int(buttonCode)] = 0
            
            clients[index2][2].send(response5.encode("utf-8"))
            clients[index2][2].send(buttonCode.encode("utf-8"))

            isOver = checkTurn(game_map, 0)
            isDraw = DrawCheck(game_map)

            if isOver:
                gameOver = True
                time.sleep(0.25)
                newClientHandler1 = threading.Thread(target=clientHandler, args=(clients[index1][2], clients[index1][0], ))
                newClientHandler1.start()

                newClientHandler1 = threading.Thread(target=clientHandler, args=(clients[index2][2], clients[index2][0], ))
                newClientHandler1.start()

                clients[index1][2].send(response6.encode("utf-8"))
                clients[index1][2].send(winCode.encode("utf-8"))

                clients[index2][2].send(response6.encode("utf-8"))
                clients[index2][2].send(loseCode.encode("utf-8"))

                clients[index1][1] = False
                clients[index2][1] = False

            if isDraw:
                gameOver = True
                time.sleep(0.25)
                newClientHandler1 = threading.Thread(target=clientHandler, args=(clients[index1][2], clients[index1][0], ))
                newClientHandler1.start()

                newClientHandler1 = threading.Thread(target=clientHandler, args=(clients[index2][2], clients[index2][0], ))
                newClientHandler1.start()

                clients[index1][2].send(response6.encode("utf-8"))
                clients[index1][2].send(drawCode.encode("utf-8"))

                clients[index2][2].send(response6.encode("utf-8"))
                clients[index2][2].send(drawCode.encode("utf-8"))

                clients[index1][1] = False
                clients[index2][1] = False

            index1Turn = False
            index2Turn = True
            continue

        if index2Turn == True:
            buttonCode = clients[index2][2].recv(1024).decode("utf-8")

            if buttonCode == request1:
                continue

            game_map[int(buttonCode)] = 1
            
            clients[index1][2].send(response5.encode("utf-8"))
            clients[index1][2].send(buttonCode.encode("utf-8"))

            isOver = checkTurn(game_map, 1)
            isDraw = DrawCheck(game_map)

            if isOver:
                gameOver = True
                time.sleep(0.25)
                newClientHandler1 = threading.Thread(target=clientHandler, args=(clients[index1][2], clients[index1][0], ))
                newClientHandler1.start()

                newClientHandler1 = threading.Thread(target=clientHandler, args=(clients[index2][2], clients[index2][0], ))
                newClientHandler1.start()

                clients[index2][2].send(response6.encode("utf-8"))
                clients[index2][2].send(winCode.encode("utf-8"))

                clients[index1][2].send(response6.encode("utf-8"))
                clients[index1][2].send(loseCode.encode("utf-8"))

                clients[index1][1] = False
                clients[index2][1] = False

            if isDraw:
                gameOver = True
                time.sleep(0.25)
                newClientHandler1 = threading.Thread(target=clientHandler, args=(clients[index1][2], clients[index1][0], ))
                newClientHandler1.start()

                newClientHandler1 = threading.Thread(target=clientHandler, args=(clients[index2][2], clients[index2][0], ))
                newClientHandler1.start()

                clients[index1][2].send(response6.encode("utf-8"))
                clients[index1][2].send(drawCode.encode("utf-8"))

                clients[index2][2].send(response6.encode("utf-8"))
                clients[index2][2].send(drawCode.encode("utf-8"))

                clients[index1][1] = False
                clients[index2][1] = False

            index1Turn = True
            index2Turn = False
            continue     

def clientHandler(client_socket, name): 
    threadIsStopped = False   
    try:
        while True and not threadIsStopped:
            request = client_socket.recv(64).decode("utf-8")
            #Если пришел запрос на получение клиентов
            if request == request1:
                data = ""
                for client in clients:
                    if client[1] == False:
                        data = data + client[0] + " "
                client_socket.send(response1.encode('utf-8'))
                client_socket.send(data.encode("utf-8"))
            #Если пришел запрос на отправку приглашения игроку
            if request == request2:
                opponentName = client_socket.recv(1024).decode("utf-8")
                for client in clients:
                    if client[0] == opponentName.split()[0]:
                        client[2].send(response2.encode('utf-8'))
                        client[2].send(opponentName.split()[1].encode("utf-8"))
            #Если пришел запрос на отправку ответа на приглашение игроку
            if request == request3:
                code = client_socket.recv(64).decode("utf-8")
                opponentName = client_socket.recv(1024).decode("utf-8")
                #Если игрок не согласился, отправляем информацию об этом
                if code == error_code:
                    for client in clients:
                        if client[0] == opponentName:
                            client[2].send(response3.encode("utf-8"))
                            client[2].send(error_code.encode("utf-8"))
                            break
                #Если игрок согласился, отправляем информацию об этом
                if code == acknowledge_code:
                    index1 = None
                    index2 = None
                    for client in clients:
                        if client[0] == opponentName:
                            #Получаем индекс клиента, отправившего приглашение на игру
                            index1 = clients.index(client)
                            client[2].send(response3.encode("utf-8"))
                            client[2].send(acknowledge_code.encode("utf-8"))
                            client[1] = True
                        if client[2] == client_socket:
                            #Получаем индекс клиента, получившего приглошение в игру
                            index2 = clients.index(client)
                            client[1] = True
                    
                    threadIsStopped = True

                    newGameHandler = threading.Thread(target=gameHandler, args=(index1, index2, ))
                    newGameHandler.start()
            #Если пришел запрос на отановку потока
            if request == request4:
                threadIsStopped = True

                
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