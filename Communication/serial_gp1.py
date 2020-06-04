from tkinter import *
from tkinter import filedialog
import serial
import tkinter.scrolledtext as tkscrolledtext
import os
import time
from serial.tools import list_ports
import threading

root = Tk()
root.wm_title("Serial v1.0 - Aziz S")
ser = serial.Serial()
txt_data = None
is_reading=False
encoding = 'utf-8'
speed = 0.1

def openser():
    global ser, is_reading
    is_reading=False
    if ser==None:
        print("No Serial Port initialised")
        return None
    if openser_button.cget("text") == "Open Serial":
        set_Port()
        print("Opening Serial Port {0}".format(defineCom.cget("text")))
        ser.open()
        openser_button.config(text='Close Serial')
        # textbox.insert('1.0', "COM Port {} Opened\r\n".format(comPort.get()))
    elif openser_button.cget("text") == "Close Serial":
        print("Closing Serial Port {0}".format(defineCom.get()))
        ser.close()
        openser_button.config(text='Open Serial')
        # textbox.insert('1.0',"COM Port {} Closed\r\n".format(comPort.get()))

def set_Port():
    global ser, is_reading
    is_reading=False
    ser.port = str(defineCom.get())
    ser.baudrate=int(defineBaud.get())
    ser.timeout=0.1
    print("PORT {0} set with baudrate = {1}".format(str(defineCom.get()),int(defineBaud.get())))

def opentxt():
    global txt_data, is_reading
    is_reading=False
    if open_txtbut.cget("text") == "Open Text file":
        filename = filedialog.askopenfilename(initialdir=os.path.realpath(".."), title="Select file",
                                              filetypes=(("text files", "*.txt"), ("all files", "*.*")))
        # print(filename)
        if filename!='':
            txt_data = open(filename, 'r')
            print("Text file is opened")
            open_txtbut.config(text='Close Text file')
            return
    # elif open_txtbut.cget("text") == "Close Text file":
    else:
        if txt_data!=None:
            print("Text file Closed!")
            txt_data.close()
            open_txtbut.config(text='Open Text file')
            return

def _quit(root):
    """Quitte l'interface"""
    global is_reading
    is_reading=False
    if txt_data!=None:txt_data.close()
    if ser.is_open: ser.close()
    root.quit()  # stops mainloop
    root.destroy()

def read_port(debut):
    global ser
    is_reading=True
    duree = 10
    while (time.time()-debut)<duree:
        if ser.readline()!="":
            data = ser.readline().decode(encoding)
            # print(data)
            if data =='exit':
                ser.close()
                print("Closed")
            elif data!="":
                to_textbox(data)
                print(data)

def read_port_thread():
    global ser, is_reading
    while is_reading:
        if ser.readline()!="":
            data = ser.readline().decode(encoding)
            print(data)
            to_textbox(data)
    print("Done reading")

def read_thread():
    global is_reading
    if Receive_button.cget("relief")==RAISED:
        if ser.is_open:
            is_reading=True
            Receive_button.config(relief=SUNKEN)
            thread = threading.Thread(target=read_port_thread)
            thread.start()
    else:
        is_reading=False
        Receive_button.config(relief=RAISED)


def send_data():
    global ser, is_reading
    # def send_thread():
    #     if ser.is_open:
    #         # for k in range(1000):
    #         #     send = str(k)+"\n"
    #         #     ser.write(send.encode('ascii'))
    #         for line in txt_data.readlines():
    #             ser.write(line.encode(encoding))
    # thread=threading.Thread(target=send_thread)
    # thread.start()
    if ser.is_open:
        # for k in range(1000):
        #     send = str(k)+"\n"
        #     ser.write(send.encode('ascii'))
        for line in txt_data.readlines():
            ser.write(line.encode(encoding))
            # time.sleep(0.3)


def get_ports():
    ports = list_ports.comports()
    textbox.insert('1.0', "Ports are")
    for port in ports:
        data = port.device+"\n"
        to_textbox(data)

def to_textbox(texte):
    textbox.insert('1.0', texte)

# Set buttons

comFrame = Frame(root)
Label(comFrame, text="COM Port :").pack(side=LEFT)
defineCom = Entry(comFrame)
defineCom.insert('0',"COM1")
defineCom.pack(side = LEFT)

Label(comFrame, text="Baudrate :").pack(side=LEFT)
defineBaud = Entry(comFrame)
defineBaud.insert('0',9600)
defineBaud.pack(side=LEFT)
comFrame.grid(row=0)

setFrame = Frame(root)
openser_button = Button(setFrame, text="Open Serial", command=openser)
openser_button.pack(side = LEFT)
setFrame.grid(row=1)
Button(setFrame, text="Ports", command=get_ports).pack(side=LEFT)
open_txtbut = Button(root, text ="Open Text file", command=opentxt)
open_txtbut.grid(row=2, column =0, columnspan=2)

sendrecFrame = Frame(root)
Button(sendrecFrame, text="Send",command=send_data).pack(side=LEFT)
Receive_button = Button(sendrecFrame, text="Receive",command=read_thread)
Receive_button.pack(side=LEFT)
sendrecFrame.grid(row=3)

frame = Frame(root, bg='cyan')
frame.grid(row=4, column=0, columnspan=3)
textbox = tkscrolledtext.ScrolledText(master=frame, wrap='word', width=30, height=5) #width=characters, height=lines
textbox.grid(row=4, column=0, columnspan=3)

quit_but = Button(root, text = "Quit", command=lambda : _quit(root))
quit_but.grid(row=5, column =0, columnspan=3)



root.mainloop()