from datetime import datetime
import os
import socket
import threading
from time import sleep
import tkinter as tk
from tkinter import TOP, Button, constants
from tkinter import scrolledtext as st, HORIZONTAL, ALL
from tkinter import Label
from tkinter import messagebox
from tkinter import filedialog
from tkinter.filedialog import askopenfile, askopenfilename
from PIL import Image, ImageTk



FONT = ("Helvetica", 18)
SMALL_FONT = ("Helvetica", 15)
BTN_FONT = ("Helvetica", 16)

HOST = '192.168.43.190'
PORT = 17034
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
state = 0
count = 50
gelen_image_name = []
gelen_image_name_y_coordinate = []

username = ''

root = tk.Tk()
root.geometry("700x720")
root.title("İLHAN")
root.resizable(False, False)
######################################################################
def hand_shake():
    try:
        client.connect((HOST, PORT))
        
    except Exception:
        messagebox.showerror("Connection Error!", "Unable to connect to server.")

    username = username_textbox.get()
    if username != '':
        client.sendall(username.encode('utf-8'))
        username_textbox.delete(0, len(username))
    else:
        messagebox.showerror("Username Error!", "Username cannot be empty.")
        exit(0)

    listen = threading.Thread(target=listen_for_messages)
    listen.start()
    
    remove_login_frame()
######################################################################
def remove_login_frame():
    username_label.destroy()
    username_textbox.destroy()
    join_btn.destroy()
######################################################################
def send_message():
    message = message_textbox.get()
    if message != '':
        msg = 'TEXT'
        client.sendall(msg.encode('utf-8')) 
        sleep(0.2)
        client.sendall(message.encode('utf-8'))   
        message_textbox.delete(0, len(message))
######################################################################
def upload_image():
    global img
    global username
    count = 0
    f_types = [('Jpg Files', '*.jpg'),('PNG Files','*.png')]  
    filename = filedialog.askopenfilename(filetypes=f_types)
    client.send('IMAGE'.encode('utf-8'))
    sleep(0.2)
    client.send(str(os.path.getsize(filename)).encode('utf-8'))
    sleep(0.2)
    with open(filename, 'rb') as file:
        for _ in range(int(os.path.getsize(filename))):
            if count < int(os.path.getsize(filename)):
                image_data = file.read(2048)
                client.send(image_data)
                count += 2048
######################################################################
def add_message_to_screen(msg):
    global count

    count += 10
    canvas.create_text(40, count, text=msg)
    count += 10
    canvas.config(scrollregion=canvas.bbox(ALL))    

######################################################################
def listen_for_messages():
    global count
    while True:
        message = client.recv(2048).decode('utf-8')
        if (message == 'TEXT'):
            text_message = client.recv(2048).decode('utf-8')
            username = text_message.split(':')[0] 
            msg = text_message.split(':')[1]
            add_message_to_screen(f"{username}:{msg}")

        elif (message == 'IMAGE'):

            username = client.recv(2048).decode('utf-8')
            add_message_to_screen(f"{username}:")
            sleep(0.2)
            size = client.recv(2048).decode('utf-8')
            sleep(0.2)
            total = 0
            alinan_resim = f'{str(datetime.now().time())}.jpg'
            with open(alinan_resim, "wb") as file:
                for _ in range(int(size)):
                    if total < int(size):
                        image_chunk = client.recv(2048)
                        file.write(image_chunk)
                        total += 2048
            sleep(0.3)
            img=Image.open(alinan_resim)
            img_resized=img.resize((400,400))
            img=ImageTk.PhotoImage(img_resized)
            gelen_image_name.append(img)
            count+= 198
            gelen_image_name_y_coordinate.append(count)
            for i in range(len(gelen_image_name)):
                canvas.create_image((40,gelen_image_name_y_coordinate[i]), image=gelen_image_name[i], tag="smile")
            count += 200
            canvas.config(scrollregion=canvas.bbox(ALL))
#####################################################################
#                           FRAME                                   #
#####################################################################
username_label = tk.Label(root, text="Username:", font=FONT, bg="white"
, fg="black")
username_label.place(relx=0.01, rely=0.01, width=250, height=50)

username_textbox = tk.Entry(root, font=FONT, bg='white', fg='black', width=15)
username_textbox.place(relx=0.42, rely=0.01, width=250, height=50)

img=Image.open('./buttons/join.png')
img_resized=img.resize((42,42))

join=ImageTk.PhotoImage(img_resized)

join_btn = tk.Button(root, text="Join", font=BTN_FONT,image=join, bg='green', fg='black', command=hand_shake)
join_btn.place(relx=0.85, rely=0.01, width=50, height=50)

# Lower frame widgets configs
message_textbox = tk.Entry(root, font=FONT, bg='white', fg='black', width=28)
message_textbox.place(relx=0.01, rely=0.94, width=500, height=30)

img=Image.open('./buttons/photos.png')
img_resized=img.resize((42,42))

photo=ImageTk.PhotoImage(img_resized)

choose_image_btn = tk.Button(root, text='Send image',font=BTN_FONT, bg="white", image=photo, fg='black', command=upload_image)
choose_image_btn.place(relx=0.75, rely=0.93) 

img=Image.open('./buttons/send.png')
img_resized=img.resize((42,42))

send=ImageTk.PhotoImage(img_resized)

send_btn = tk.Button(root, text="Send", font=BTN_FONT, image=send,  fg='black', command=send_message)
send_btn.place(relx=0.85, rely=0.93)

canvas = tk.Canvas(root, bg='white', width=630, height=590)
canvas.place(relx=0.01, rely=0.1)

scrollbar_y = tk.Scrollbar(root)
scrollbar_y.place(relx=0.91, rely=0.1, width=20, height=590)
scrollbar_y.config(command=canvas.yview)

scrollbar_message_x = tk.Scrollbar(root, orient=HORIZONTAL)
scrollbar_message_x.place(relx=0.01, rely=0.90, width=630, height=20)
scrollbar_message_x.config(command=canvas.xview)

canvas.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_message_x.set)
#####################################################################

def main():
    root.mainloop()

# driver function
if __name__ == '__main__':
    main()
