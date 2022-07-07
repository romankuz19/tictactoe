from tkinter import *
from tkinter import messagebox
import time, socket, threading

SERVER_ADDRESS = ("127.0.0.1", 11000)
CLIENT_NAME = ""

error_code = '54a0e8c17ebb21a11f8a25b8042786ef7efe52441e6cc87e92c67e0c4c0c6e78' #Код ощибки
acknowledge_code = 'f9236d9e87b6235ec4f2d7e00d60f5a68670c6dcf70f6f2f354a4325f79f1b27' #Код подтверждения

request1 = 'b06aa45eb35423f988e36c022967b4c02bb719b037717df13fa57c0f503d8a20' #Код запроса на получение списка свободных игроков

root = Tk()
root.title("Tic-tac-toe")
root.geometry('450x500')
root.resizable(width=False, height=False)
root.configure(bg="grey")

#Функция в дополнительном потоке производит динамическое обновление списка игроков
def getFreeClients(client_socket, listbox):
    free_clients1 = []
    free_clients2 = []
    result = []

    while True:
        time.sleep(0.75)
        client_socket.send(request1.encode("utf-8"))
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

#Интерфейс вывода свободных игроков
def drawPlayerSelector():
    label2 = Label(text=f"Hello, {CLIENT_NAME}!\nSelect player..",fg="white", bg="grey", font=('Arial', 20, 'bold'))
    label2.pack()

    scrollbar = Scrollbar(root)
    scrollbar.place(x=430, y=80, height=395)

    listbox = Listbox(width=38, height=17, yscrollcommand=scrollbar.set, font=('Arial', 14, 'bold'))  

    listbox.place(x=5, y=80)
    scrollbar.config(command=listbox.yview)

    getingFreeClients = threading.Thread(target=getFreeClients, args=(client_socket, listbox, ))
    getingFreeClients.start()

#Обработчик нажатия на кнопку button1
def joinClick():
    global CLIENT_NAME, entry1, client_socket
    CLIENT_NAME = entry1.get()
    if not CLIENT_NAME:
        messagebox.showerror("Error!", "Please, enter your name!")
    else: 
        #Конектимся к серверу
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(SERVER_ADDRESS)
        client_socket.send(CLIENT_NAME.encode("utf-8"))
        code = client_socket.recv(1023).decode("utf-8")
        #Если пришло подтверждение перерисовываем интерфейс 
        if code == acknowledge_code:
            label1.destroy()
            entry1.destroy()
            button1.destroy()

            drawPlayerSelector()
        #Если пришел код ошибки, оставляем интерфейс
        if code == error_code:
            messagebox.showerror("Error!", "Such name already exists!")
            client_socket.close()
            
#Отрисовка интерфейса ввода имени пользователя            

label1 = Label(text="Welcome to еру tic-tac-toe game!\nPlease, enter your name!", fg="white", bg="grey", font=('Arial', 20, 'bold'))
label1.pack()

entry1 = Entry(root, width=20, font=('Arial', 14, 'bold')) #font=('Arial', 14, 'bold')
entry1.place(relx = 0.25, rely=0.3)

button1 = Button(width=7, height=1, font=('Arial', 10, 'bold'), text="Join!", command=joinClick)
button1.place(relx = 0.43, rely=0.4)

root.mainloop()
