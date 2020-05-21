import speech_recognition as sr
from tkinter import *
from PIL import ImageTk ,Image
import os
import re

cwd_path = os.getcwd()
Rotation_Regex = re.compile(r'(rotation|rot)? (\d*) (degrees|radian|rad)?')

def init_image(path, size=(28,28)):
    img = Image.open(cwd_path+path)
    img= img.resize(size)
    return ImageTk.PhotoImage(img)

class Srwindow():

    def __init__(self, root, window):
        self.root = root
        self.window = window
        self.set_buttons(self.window)



    def set_buttons(self, window):
        record_button = Button(master=window,text="Record",image = record_ico,  command=self.reco).pack(side=LEFT)
        self.cmdentry = Entry(master=window)
        self.cmdentry.pack(side=LEFT)
        Button(master=window, text="Confirm", command=self.confirm, image=play_ico).pack(side=LEFT)
        Button(master=window, text="Export", command=self.export).pack(side = LEFT)
        return 0

    def reco(self):
        self.cmdentry.delete(0,END)
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say Something!")
            self.cmdentry.insert(0,"Recording!")
            audio = r.listen(source)
        try:
            print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
            txt=r.recognize_google(audio)
            self.cmdentry.delete(0,END)
            self.cmdentry.insert(0, txt)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        self.to_command(txt)
        return 0

    def to_command(self, text):
        consigne = Rotation_Regex.search(text).group(2)
        print("on reconnait une rotation de :", consigne)

    def confirm(self):
        return 0
    def export(self):
        return 0

root = Tk()
Button(root, text="quit", command = root.quit).pack()

play_ico=init_image(r'\icon\play.png')
record_ico = init_image(r'\icon\record.png')

window = Toplevel(root)
Srwindow(root, window)
mainloop()
