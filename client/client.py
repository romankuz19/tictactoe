from tkinter import *
from tkinter import messagebox
import time, socket, threading
import tkinter

SERVER_ADDRESS = ("127.0.0.1", 11000)
CLIENT_NAME = ""

stopRequest1 = False
stopWaitingTimer = False
timeIsOver = False

label2 = None
scrollbar = None
listbox = None
button2 = None
buttons = None

free_clients1 = []
free_clients2 = []
result = []

PLAYER_SIGN = ''
TURN = False

left_buttons = None

error_code = '54a0e8c17ebb21a11f8a25b8042786ef7efe52441e6cc87e92c67e0c4c0c6e78' #Код ощибки
acknowledge_code = 'f9236d9e87b6235ec4f2d7e00d60f5a68670c6dcf70f6f2f354a4325f79f1b27' #Код подтверждения

request1 = 'b06aa45eb35423f988e36c022967b4c02bb719b037717df13fa57c0f503d8a20' #Код запроса на получение списка свободных игроков
request2 = '2fc41ef02a3216e4311805a9a11405a41a8d7a9f179526b4f6f2866bff009a10' #Код запроса на отпраку приглашения пользователю
request3 = '3ff16f0155fae419d7c1402dd267a146bba71abaabb5c3d29477aa54729f3472' #Код запроса на отправку ответа на приглашение игроку

request4 = '70337a34b6415ba5fa027f5db805f9393636c6e39de7a76a6ef64398622d2c74' #Код запроса на ход

response1 = '9e60b7bc9a12f2f193a91b7e41401de9cdf0bdae7f3670cc91634a5b4ceb5e19' #Код ответа на запрос на получение списка свободных игроков
response2 = 'ada2e137475fbfd01168a228fbe0a38a4cee57894ba2ffec5ec9e5c6a5d91156' #Код ответа на запрос на отправку приглашения игроку
response3 = 'c843750529bac77ebc4e2026642fd03c048682b9c98963bb1a938c632b64ab71' #Код ответа на запрос на отправку ответа на приглашение игрока

response4 = '5b828eacedee30f2ea5a6e7fc2e0323ddc6350ab2d7540b08982e3120afb12dd' #Код ответа на получение крестика или нолика
response5 = '838c118150d2f7b40272b6aee2492357b77dfc870209ca9df9cae280e0d5076c' #Код ответа на получение хода противника
response6 = '144a5931ec80d672f104cc4c7e6b978b825ac06df0d7c5774ab7994a35ebcb50' #Код ответа о выигрыше или проигрыше

winCode = '0713d07cd82977b5de4dba918140019fbfecf9883b13ea58f7f2c54f121bb06a' #Код победы
loseCode = 'cc8a30ea6faccd1bd3503e5a9001bbac91871be28a2140be347b2cc9d27d8031' #Код порожения
drawCode = '50f7becde477bb509c7704de62c349247fb3499c03a95e4bce20151cd552dea5' #Код ничьей

root = Tk()
root.title("Tic-tac-toe")
root.geometry('450x500')
root.resizable(width=False, height=False)
root.configure(bg="grey")

def getClientsList(client_socket):
    global stopRequest1
    while not stopRequest1:
        time.sleep(0.05)
        client_socket.send(request1.encode("utf-8"))

#Обработчик нажатия на кнопку button1
def joinClick():
    global CLIENT_NAME
    def push(number):
        global buttons, left_buttons, PLAYER_SIGN
        buttons[number].config(text=PLAYER_SIGN, state="disabled", bg="white")
        left_buttons.remove(number)

        client_socket.send(str(number).encode("utf-8"))

        for button in buttons:
            button.config(state='disabled')

    #Функция отрисовки поля игры
    def drawPlayingField():
        global buttons
        time.sleep(0.25)

        label2.destroy()
        scrollbar.destroy()
        listbox.destroy()
        button2.destroy()

        root.geometry('442x500')
        
        buttons = [Button(width=6, height=3, font=('Arial', 28, 'bold'), bg='gray', command=lambda x=i: push(x)) for i in range(9)]

        row = 1
        col = 0

        for i in range(9):
            buttons[i].grid(row=row, column=col)
            col += 1
            if col == 3: 
                row += 1
                col = 0

    def countdown(num_of_secs):
        global stopWaitingTimer, timeIsOver, label2, scrollbar, listbox, button2, free_clients1, free_clients2, result

        label2.destroy()
        scrollbar.destroy()
        listbox.destroy()
        button2.destroy()

        stopWaitingTimer = False
        timeIsOver = False

        label3 = Label(text=f"Waiting for the player's response!",fg="white", bg="grey", font=('Arial', 20, 'bold'))
        label3.place(x=3, y=200) 

        textTimer = tkinter.StringVar()
        textTimer.set("00:00")

        label4 = Label(fg="white", bg="grey", font=('Arial', 20, 'bold'), textvariable=textTimer)
        label4.place(x=180, y=250) 

        while num_of_secs and not stopWaitingTimer:
            m, s = divmod(num_of_secs, 60)
            min_sec_format = '{:02d}:{:02d}'.format(m, s)
            textTimer.set(f"{min_sec_format}")
            time.sleep(1)
            num_of_secs -= 1
            
        timeIsOver = True
        label4.destroy()
        label3.destroy()

        if not stopWaitingTimer:
            free_clients1.clear()
            free_clients2.clear()
            result.clear()
            drawPlayerSelector()

    #Функция в дополнительном потоке производит динамическое обновление списка игроков
    def serverListener(client_socket):
        global stopRequest1, timeIsOver, stopWaitingTimer, listbox, label2, scrollbar, button2, free_clients1, free_clients2, result, PLAYER_SIGN, TURN, left_buttons
        while True:
            response = client_socket.recv(1024).decode("utf-8")

            if response == response1:
                free_clients = client_socket.recv(1024).decode("utf-8")
                free_clients1 = free_clients.split()

                #То, что надо добавить (разность free_client1 и free_client2)
                result = list(set(free_clients1) - set(free_clients2))

                if result:
                    for client in result:
                        if client == CLIENT_NAME: 
                            continue
                        else:
                            listbox.insert(END, client)

                #То, что надо удалить (разность free_client2 и free_client1)
                result = list(set(free_clients2) - set(free_clients1))

                if result:
                    for client in result:
                        index = listbox.get(0, "end").index(client)
                        listbox.delete(index)
                free_clients2 = free_clients1
            if response == response2:
                opponentName = client_socket.recv(1024).decode("utf-8")
                question = messagebox.askquestion("invitation", f"The player {opponentName} invites you to play..\nDo you want to play?")
                #Если согласны, отправляем подтверждение
                if question == 'yes':
                    client_socket.send(request3.encode("utf-8"))
                    client_socket.send(acknowledge_code.encode("utf-8"))
                    client_socket.send(opponentName.encode("utf-8"))
                    stopRequest1 = not stopRequest1
                    drawPlayingField()
                #Если не согласны, отправляем ошибку
                if question == 'no':
                    client_socket.send(request3.encode("utf-8"))
                    client_socket.send(error_code.encode("utf-8"))
                    client_socket.send(opponentName.encode("utf-8"))
            if response == response3:
                code = client_socket.recv(64).decode("utf-8")
                if code == error_code:
                    #Проверяем отсчитал лм таймер (Если отсчитал - пропускаем)
                    if timeIsOver:
                        pass
                    #Если не отсчитал останавливаем и перерисовываем итерфейс
                    if not timeIsOver:
                        stopWaitingTimer = True

                        free_clients1.clear()
                        free_clients2.clear()
                        result.clear()

                        drawPlayerSelector()
                        messagebox.showinfo("Information", "The user did not agree to play..")
                if code == acknowledge_code:
                    #Проверяем отсчитал лм таймер (Если отсчитал - пропускаем)
                    if timeIsOver:
                        pass
                    #Если не отсчитал останавливаем и перерисовываем итерфейс
                    if not timeIsOver:
                        stopWaitingTimer = True
                        #Прерываем поток, в котором запрашиваются свободные пользователи и переводим интерфейс в ожидание
                        
                        client_socket.send(request4.encode("utf-8"))

                        stopRequest1 = not stopRequest1
                        drawPlayingField()
            if response == response4:
                PLAYER_SIGN = client_socket.recv(1).decode("utf-8")
                TURN = int(client_socket.recv(1).decode("utf-8"))

                left_buttons = list(range(9))

                if bool(TURN) == True:
                    messagebox.showinfo("Welcome to the game!", f"You is {PLAYER_SIGN}!\nYour turn!")
                if bool(TURN) == False:
                    messagebox.showinfo("Welcome to the game!", f"You is {PLAYER_SIGN}!\nOpponent turn!")
                    for button in buttons:
                        button.config(state='disabled')
            if response == response5:
                buttonCode = client_socket.recv(1024).decode("utf-8")
                if PLAYER_SIGN == 'X':
                    buttons[int(buttonCode)].config(text='O', state="disabled", bg="white")
                    left_buttons.remove(int(buttonCode))
                if PLAYER_SIGN == 'O':
                    buttons[int(buttonCode)].config(text='X', state="disabled", bg="white")
                    left_buttons.remove(int(buttonCode))
                for button in buttons:
                    if buttons.index(button) in left_buttons:
                        button.config(state='normal')
            if response == response6:
                code = client_socket.recv(1024).decode("utf-8")
                
                for button in buttons:
                    button.destroy()

                free_clients1.clear()
                free_clients2.clear()
                result.clear()

                root.geometry('450x500')

                drawPlayerSelector()

                if code == winCode:
                    messagebox.showinfo("Win", "You Win!")
                if code == loseCode:
                    messagebox.showinfo("Lose", "You Lose!")
                if code == drawCode:
                    messagebox.showinfo("Draw", "It's draw!")
                
    def startGame(client_socket):
        global stopRequest1, stopWaitingTimer, timeIsOver, scrollbar, listbox, button2, label2

        if not listbox.curselection():
            messagebox.showerror("Error!", "Please, choose an opponent!")
        else:
            #Прерываем поток, в котором запрашиваются свободные пользователи и переводим интерфейс в ожидание
            stopRequest1 = not stopRequest1

            listbox_txt = listbox.get(listbox.curselection())+ ' ' + CLIENT_NAME

            client_socket.send(request2.encode("utf-8"))
            client_socket.send(listbox_txt.encode("utf-8"))

            #Запускаем таймер отсчета ожидания
            newCounter = threading.Thread(target=countdown, args=(30, ))
            newCounter.start()


    #Функция отрисовки интерфеса выбора свободного игрока
    def drawPlayerSelector():
        global stopRequest1, scrollbar, listbox, button2, label2

        label1.destroy()
        entry1.destroy()
        button1.destroy()

        label2 = Label(text=f"Hello, {CLIENT_NAME}!\nSelect player..",fg="white", bg="grey", font=('Arial', 20, 'bold'))
        label2.pack()

        scrollbar = Scrollbar(root)
        scrollbar.place(x=430, y=80, height=349)

        listbox = Listbox(width=38, height=15, yscrollcommand=scrollbar.set, font=('Arial', 14, 'bold'), selectmode=SINGLE)  

        listbox.place(x=5, y=80)
        scrollbar.config(command=listbox.yview)

        button2 = Button(width=7, height=1, font=('Arial', 10, 'bold'), text="Play!", command=lambda: startGame(client_socket))
        button2.place(relx = 0.43, rely=0.9)

        stopRequest1 = False

        #Открываем поток, в котором получаем список свободных игроков
        newGetingClientsThread = threading.Thread(target=getClientsList, args=(client_socket, ))
        newGetingClientsThread.start()

    CLIENT_NAME = entry1.get()
    if not CLIENT_NAME:
        messagebox.showerror("Error!", "Please, enter your name!")
    else: 
        #Конектимся к серверу
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(SERVER_ADDRESS)
        client_socket.send(CLIENT_NAME.encode("utf-8"))
        code = client_socket.recv(1024).decode("utf-8")
        #Если пришло подтверждение перерисовываем интерфейс 
        if code == acknowledge_code:
            drawPlayerSelector()

            #Запускаем поток, в котором будем принимать ответы сервера
            newServerListener = threading.Thread(target=serverListener, args=(client_socket, ))
            newServerListener.start()

        #Если пришел код ошибки, оставляем интерфейс
        if code == error_code:
            messagebox.showerror("Error!", "Such name is already exists!")
            client_socket.close()
            
#Отрисовка интерфейса ввода имени пользователя            
label1 = Label(text="Welcome to the tic-tac-toe game!\nPlease, enter your name!", fg="white", bg="grey", font=('Arial', 20, 'bold'))
label1.pack()

entry1 = Entry(root, width=20, font=('Arial', 14, 'bold')) #font=('Arial', 14, 'bold')
entry1.place(relx = 0.25, rely=0.3)

button1 = Button(width=7, height=1, font=('Arial', 10, 'bold'), text="Join!", command=joinClick)
button1.place(relx = 0.43, rely=0.4)

root.mainloop()