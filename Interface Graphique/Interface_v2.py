import os
import re
# Interface Tools and libraries
import tkinter
import tkinter.scrolledtext as tkscrolledtext
import matplotlib.pyplot as plt
import numpy as np
import speech_recognition as sr  # PyAudio is needed
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

# Import simu_superpo
filepath = os.path.realpath("..")+r"\Simulations"+"\\"
import sys
sys.path.append(filepath)


# Modeles de reconnaissance de commande pour la commande Vocale
Rotation_Regex = re.compile(r'(rotation|rot)')
Sclock_Regex = re.compile(r'(clock.*\s?|right)')
Snclock_Regex = re.compile(r'(anticlock.*\s?|left)')
LIN_Regex = re.compile(r'(line.*\s\s?|go)')
SLIN_Regex = re.compile(r'(back.*\s\s?)')
digit_regex = re.compile(r'\d{1,3}')


class Interface():
    # VARIABLES
    FIGSIZE = (5, 4)
    DPI = 100
    DRAW_METHOD = 1  # Permet à l'interface de choisir entre les methodes de trace (LIN,CIR)
    AXIS = [-5, 5, -1, 5]  # Definit l'espace de travail du robot
    GRID = True  # Definit la presence ou non de la grille
    VOICE_RECO = True

    def __init__(self):
        """Initialisation de Tkinter"""
        self.root = tkinter.Tk()
        self.root.wm_title("Interface Commande Robot")
        self.fig = Figure(figsize=self.FIGSIZE, dpi=self.DPI)
        self.ax = self.fig.add_subplot(111)
        self.robot_im = plt.imread('robot.png')
        self.imgplot = self.ax.imshow(self.robot_im, origin=(0, 0), extent=([-1, 1, -1, 1]))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)

        self.setup()
        # Variables
        self.init_graph()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        'connect to all the events we need'
        self.press=None
        self.canvas.mpl_connect("button_press_event", self.on_key_press)
        self.cidrelease = self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.textbox = tkscrolledtext.ScrolledText(master=self.root, wrap='word', height=2)
        self.textbox.pack(side=tkinter.TOP, fill='x', expand=1)
        self.set_buttons()

    def setup(self):
        """Mise en place de la Figure Matplotlib"""
        self.ax.axis(self.AXIS)

        self.set_grid()

        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.toolbar.update()

    def set_grid(self):
        """Mise en place de la grille"""
        if self.GRID:
            # Major ticks, minor ticks every
            major_ticks = np.arange(self.AXIS[0], self.AXIS[1], 1)

            self.ax.set_xticks(major_ticks)
            self.ax.set_yticks(major_ticks)

            # And a corresponding grid
            self.ax.grid(which='both', alpha=0.2)
            self.ax.set_axisbelow(True)

    def set_buttons(self):
        """Mise en place des boutons sur Tkinter"""
        self.query_frame = tkinter.Frame(self.root)

        self.window_button = tkinter.Button(self.query_frame, text="Command Window", command=self.command_window)
        self.window_button.pack(side=tkinter.LEFT)

        self.update_linmethodbutton = tkinter.Button(master=self.query_frame, text="Line",
                                                     command=lambda :self.change_method(1), relief=tkinter.SUNKEN)
        self.update_linmethodbutton.pack(side=tkinter.LEFT)

        self.update_cirmethodbutton = tkinter.Button(master=self.query_frame, text="CIR",
                                                     command=lambda : self.change_method(2))
        self.update_cirmethodbutton.pack(side=tkinter.LEFT)

        self.update_freemethodbutton = tkinter.Button(master=self.query_frame, text="Free",
                                                     command=lambda : self.change_method(3))
        self.update_freemethodbutton.pack(side=tkinter.LEFT)

        self.erase_methodbutton = tkinter.Button(master=self.query_frame, text="Erase",
                                                 command=self.erase_plt)
        self.erase_methodbutton.pack(side=tkinter.LEFT)

        self.pos_button = tkinter.Button(master=self.query_frame, text="Simulation", command=self.Simulation)
        self.pos_button.pack(side=tkinter.LEFT)

        self.export_button = tkinter.Button(master=self.query_frame, text="Export", command=self.command_txt)
        self.export_button.pack(side=tkinter.LEFT)

        if self.VOICE_RECO:
            self.mic_button = tkinter.Button(master=self.query_frame, text="Mic", command=self.voice_command_window)
            self.mic_button.pack(side=tkinter.LEFT)

        self.precision_scale = tkinter.Scale(self.query_frame,from_=1, to=20, orient = "horizontal", tickinterval=2, length=100,label='Precision')
        self.precision_scale.pack(side=tkinter.LEFT)

        self.query_frame.pack(side=tkinter.LEFT)

        self.quit_button = tkinter.Button(master=self.root, text="Quit", command=self._quit)
        self.quit_button.pack(side=tkinter.BOTTOM)

    def init_graph(self):
        """Initialise la courbe de la trajectoire, ainsi que les commandes et les directions"""
        self.plt_draw = np.zeros((1, 2))  # Coordonnées interprete par matplotlib pour le trace
        self.command = np.zeros((1, 3))
        self.directions = np.array([[0, 1]])
        self.drawing, = self.ax.plot(self.plt_draw[:, 0], self.plt_draw[:, 1])

    def erase_plt(self):
        """Reinitialise le trace"""
        self.ax.cla()
        self.init_graph()
        self.textbox.delete('1.0', tkinter.END)
        self.ax.axis(self.AXIS)
        self.set_grid()
        self.robot_im = plt.imread('robot.png')
        self.imgplot = self.ax.imshow(self.robot_im, origin=(0, 1), extent=([-1, 1, -1, 1]))
        self.update_graph()

    def on_key_press(self, event):
        """Gestion de l'evenement clic gauche et gestion du trace"""
        # print("you pressed ({0},{1})".format(event.xdata, event.ydata))
        key_press_handler(event, self.canvas, self.toolbar)
        if event.inaxes != self.ax.axes: return
        x, y = event.xdata, event.ydata
        if np.abs(x) > 10 or np.abs(y) > 10: return
        if self.DRAW_METHOD == 1:  # Ligne droite
            self.rot_lin(x, y)
        if self.DRAW_METHOD == 2:  # CIR
            self.draw_CIR(x, y)
        # Update Canvas
        self.update_graph()
        self.press = event.xdata, event.ydata

    def on_motion(self, event):
        'on motion we will move'
        if self.press is None: return
        if event.inaxes != self.ax.axes: return
        xold, yold = self.press
        precision = float(self.precision_scale.get())/10
        # precision=.5
        if self.DRAW_METHOD==3:
            dx = event.xdata - xold
            dy = event.ydata - yold
            if np.abs(np.linalg.norm((dx,dy)))>precision:
                # self.CIR(cir_entry=(event.xdata, event.ydata), entry=True)
                self.rot_lin(event.xdata, event.ydata)
                # self.add_coordinate([event.xdata, event.ydata])
                self.update_graph()
                self.add_direction([dx,dy])
                self.press =event.xdata, event.ydata

    def on_release(self, event):
        'on release we reset the press data'
        self.press = None
        self.ax.figure.canvas.draw()

    # Changement de méthode de trace

    def change_method(self, method):
        if method==1:
            self.update_linmethodbutton.config(relief=tkinter.SUNKEN)
            self.update_cirmethodbutton.configure(relief=tkinter.RAISED)
            self.update_freemethodbutton.configure(relief=tkinter.RAISED)
            self.DRAW_METHOD = 1
        elif method==2:
            self.update_cirmethodbutton.config(relief=tkinter.SUNKEN)
            self.update_linmethodbutton.configure(relief=tkinter.RAISED)
            self.update_freemethodbutton.configure(relief=tkinter.RAISED)
            self.DRAW_METHOD = 2
        else:
            self.update_freemethodbutton.config(relief=tkinter.SUNKEN)
            self.update_linmethodbutton.configure(relief=tkinter.RAISED)
            self.update_cirmethodbutton.configure(relief=tkinter.RAISED)
            self.DRAW_METHOD=3


    def Simulation(self):
        """Lance la simulation"""
        self.fig.savefig("last_figure.png")
        self._quit()
        import simu_superpo

    # Méthodes de tracé
    def ROT(self, ang_entry=0.0, entry=False):
        """Methode de Rotation de la voiture"""
        # Update direction
        if entry:
            angrad = float(ang_entry) * np.pi * 2 / 360
        else:
            angrad = float(self.thetaentry.get()) * np.pi * 2 / 360
        xdir, ydir = self.directions[-1]
        new_dir = self.rotatenp(xdir, ydir, -angrad)
        new_dir = np.array([round(new_dir[0], 2), round(new_dir[1], 2)])
        self.add_direction(new_dir)
        # Add command
        self.add_command(0, angrad, 0)
        # Plot point to show rotation
        x, y = self.plt_draw[-1]
        self.ax.plot(x, y, 'ro', alpha=0.5)
        self.update_graph()
        return 0

    def LIN(self, d_entry=0.0, entry=False):
        """Methode de ligne droite de la voiture"""
        if entry:
            d = float(d_entry)
        else:
            d = float(self.dentry.get())
        xold, yold = self.plt_draw[-1]
        xdir, ydir = self.directions[-1]
        if d > 0:
            xout = xold + d * xdir
            yout = yold + d * ydir
        else:
            xout = xold + d * xdir
            yout = yold + d * ydir
            self.add_direction(np.array([-self.directions[-1][0], -self.directions[-1][1]]))
        self.add_coordinate([xout, yout])
        self.add_command(1, d, 0)
        self.update_graph()
        return 0

    def CIR(self, cir_entry=(0,0), entry=False):
        """Méthode tracé d'arc de la voiture"""
        if entry:
            self.draw_CIR(float(cir_entry[0]), float(cir_entry[1]))
        else:
            self.draw_CIR(float(self.xcirentry.get()), float(self.ycirentry.get()))
        self.update_graph()

    def rot_lin(self, x, y):
        """Trace le LIN de la voiture"""
        dv = x - self.plt_draw[-1][0], y - self.plt_draw[-1][1]
        angle = self.get_ang(self.plt_draw[-1], np.array([x, y]), dir=True,
                             direction=self.directions[-1])  # Determination de l'angle de rotation
        # Ajout des commandes
        if np.abs(angle) > 0.01:  # Ajoute une commande de rotation s'il est non nul
            self.add_command(0, angle, 0)
        # Mise à jour de la direction
        self.add_direction(dv)
        # Ajout des coordonnees du click
        self.add_coordinate([x, y])
        # Ajout de la commande en LIN
        self.add_command(1, np.linalg.norm(dv), 0)

    def draw_CIR(self, xout, yout):
        """Trace le CIR"""
        xin, yin = self.plt_draw[-1][0], self.plt_draw[-1][1]
        xcv, ycv, sgn, x, y = self.init_arc(xout, yout)
        ang_b = self.get_ang((0, 1), (self.directions[-1][0], self.directions[-1][1]))
        if xcv == None:
            print("Invalid CIR Command")
            return
        # Changement de base du cas precedent pour le mettre en modele global
        dir_2 = self.directions[-1]
        xn, yn = list(), list()
        vn = list()
        for k in range(len(x)):
            xglob, yglob = self.changement_base(x[k], y[k], ang_b, xin, yin)
            xn.append(xglob)
            yn.append(yglob)
            if not np.isnan(xglob) and not np.isnan(yglob):
                vn.append([xglob, yglob])
        vn = np.reshape(np.array(vn), (len(vn), 2))
        self.add_coordinate(vn)
        # Mise a jour de la direction et des commandes
        dv_dir = xn[-1] - xn[-2], yn[-1] - yn[-2]
        self.add_direction(dv_dir)
        self.add_command(2, xout, yout)

    def init_arc(self, xout, yout):
        """Crée un arc dans la base de la voiture"""
        xin, yin = self.plt_draw[-1][0], self.plt_draw[-1][1]
        # Calcul dans le cas (x0,y0)=(0,0) et direction = (0,1)
        ang_b = self.get_ang((1, 0), (self.directions[-1][0], self.directions[-1][1]))
        dxr, dyr = self.rot_inv(xin, yin, xout, yout, np.pi / 2 - ang_b)
        theta_ini = 0
        Xcv = dyr * np.sin(theta_ini) + dxr * np.cos(theta_ini)
        Ycv = dyr * np.cos(theta_ini) - dxr * np.sin(theta_ini)
        if Ycv < 0: return None, None, None, None, None  # On bannit le cas ou Ycv<0
        sgn = (Xcv / np.abs(Xcv))
        R = sgn * (Xcv ** 2 + Ycv ** 2) / (2 * Xcv)
        X = np.linspace(0, Xcv, 100)
        Y = np.sqrt(R ** 2 - np.power(X - sgn * R, 2))
        return Xcv, Ycv, sgn, X, Y

    @staticmethod
    def rot_inv(xin, yin, xout, yout, theta):
        """Changement de base: De la base globale à la base de la voiture"""
        dx, dy = xout - xin, yout - yin
        dxr, dyr = -np.sin(theta) * dy + np.cos(theta) * dx, np.cos(theta) * dy + np.sin(theta) * dx
        return dxr, dyr

    @staticmethod
    def changement_base(xrel, yrel, theta, x0, y0):
        """Change la base (rotation, translation)"""
        chg_base = np.array([[np.cos(theta), -np.sin(theta), x0],
                             [np.sin(theta), np.cos(theta), y0],
                             [0, 0, 1]])
        j = np.array([[xrel],
                      [yrel],
                      [1]])
        result = np.dot(chg_base, j)
        return float(result[0]), float(result[1])

    # Méthodes géométriques
    @staticmethod
    def rotatenp(x, y, ang):
        """Use numpy to build a rotation matrix and take the dot product."""
        co, si = np.cos(ang), np.sin(ang)
        j = np.array([[co, si], [-si, co]])
        m = np.dot(j, [x, y])
        return float(m[0]), float(m[1])

    @staticmethod
    def get_ang(v1, v2, dir=False, direction=(0, 1)):
        """Determine l'angle de rotation avec consideration possible de la direction precedante"""
        vect1 = np.array([float(v1[0]), float(v1[1])])
        vect2 = np.array([float(v2[0]), float(v2[1])])
        if dir:
            vect2 = vect2 - vect1
            vect1 = np.array([float(direction[0]), float(direction[1])])
        if np.linalg.norm(vect1) * np.linalg.norm(vect2) == 0:
            print("get_ang: Invalid value")
            return 0
        v1_unit = vect1 / np.linalg.norm(vect1)
        v2_unit = vect2 / np.linalg.norm(vect2)
        dot_product = np.dot(v1_unit, v2_unit)
        sgn = v1_unit[0] * v2_unit[1] - v1_unit[1] * v2_unit[0]
        if sgn != 0:
            sgn = sgn / np.abs(sgn)
        else:
            return 0
        return sgn * np.arccos(dot_product)

    # Methodes de mise à jour des variables
    def update_graph(self):
        """Met à jour le graphique"""
        self.ax.figure.canvas.draw()

    def add_coordinate(self, data):
        """Ajoute les coordonnées au graphique"""
        self.plt_draw = np.vstack((self.plt_draw, np.array(data)))
        self.drawing.set_data(self.plt_draw[:, 0], self.plt_draw[:, 1])

    def add_command(self, c, i1, i2):
        """Met a jour la liste de commandes"""
        self.command = np.vstack((self.command, np.array([c, i1, i2])))
        command_dict = {0: 'ROT', 1: 'LIN', 2: 'CIR'}
        c = command_dict[int(self.command[-1][0])]
        self.textbox.insert('1.0',
                            "{0}({1},{2})\n".format(c, round(self.command[-1][1], 2), round(self.command[-1][2])), 2)

    def add_direction(self, dv):
        """Met à jour la liste de directions"""
        self.directions = np.vstack((self.directions, dv / np.linalg.norm(dv)))

    def command_txt(self):
        """Renvoie les commande sous forme de fichier texte, la suite du programme est gere par la partie Trajectoire"""
        path = os.getcwd()
        text_data = open(path + "\\values.txt", "w")
        command_dict = {0: 'R', 1: 'L', 2: 'A'}
        for instruct in self.command[1:-1]:
            c = command_dict[int(instruct[0])]
            txt = "{0},{1},{2};".format(c, round(instruct[1], 3), round(instruct[2], 3))
            text_data.write(txt)
        instruct = self.command[-1]
        c = command_dict[int(instruct[0])]
        txt = "{0},{1},{2}".format(c, round(instruct[1], 3), round(instruct[2], 3))
        text_data.write(txt)
        text_data.close()
        print("Commandes exportées!")
        return 0

    def _quit(self):
        """Quitte l'interface"""
        self.root.quit()  # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def command_window(self):
        """Affiche l'invité de commande LIN,CIR,ROT"""
        self.window = tkinter.Toplevel(self.root)
        self.set_windowbutton()

    def set_windowbutton(self):
        """Met en place la fenetre de commande"""
        col = 0
        tkinter.Label(self.window, text="CIR (x, y): ").grid(row=0, column=col)
        col += 1
        self.xcirentry = tkinter.Entry(self.window)
        self.xcirentry.grid(row=0, column=col)
        col += 1
        tkinter.Label(self.window, text=", ").grid(row=0, column=col)
        col += 1
        self.ycirentry = tkinter.Entry(self.window)
        self.ycirentry.grid(row=0, column=col)
        col += 1
        self.update_cirbutton = tkinter.Button(master=self.window, text="CIR", command=self.CIR)
        self.update_cirbutton.grid(row=0, column=col)
        colcir = col
        col = 0
        tkinter.Label(self.window, text="ROT° (theta): ").grid(row=1, column=col)
        col += 1
        self.thetaentry = tkinter.Entry(self.window)
        self.thetaentry.grid(row=1, column=col)
        col += 1
        self.update_rotbutton = tkinter.Button(master=self.window, text="ROT", command=self.ROT)
        self.update_rotbutton.grid(row=1, column=colcir)
        col = 0
        tkinter.Label(self.window, text="LIN (d): ").grid(row=2, column=col)
        col += 1
        self.dentry = tkinter.Entry(self.window)
        self.dentry.grid(row=2, column=col)
        col += 1
        self.update_linbutton = tkinter.Button(master=self.window, text="LIN", command=self.LIN)
        self.update_linbutton.grid(row=2, column=colcir)

    def voice_command_window(self):
        """Lance la fenêtre de commande par reconnaissance vocale"""
        self.window2 = tkinter.Toplevel()
        f = tkinter.Frame(self.window2)
        self.set_buttons_mic(f)
        f.pack()

    def set_buttons_mic(self, frame):
        """Met en place les boutons sur la fenêtre de reconnaissance vocale"""
        col = 0
        but1 = tkinter.Button(frame, text="Record", command=self.reco)
        but1.grid(row=0, column=col)
        col += 1
        self.cmdentry = tkinter.Entry(frame)
        self.cmdentry.grid(row=0, column=col)
        col += 1
        but2 = tkinter.Button(frame, text="Confirm", command=self.confirm)
        but2.grid(row=0, column=col)

    def reco(self):
        """Lance la reconnaissance vocale"""
        self.cmdentry.delete(0, tkinter.END)
        r = sr.Recognizer()
        txt = ""
        with sr.Microphone() as source:
            print("Say Something!")
            self.cmdentry.insert(0, "Recording!")
            audio = r.listen(source)
        try:
            print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
            txt = r.recognize_google(audio)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        self.v_command = self.to_command(txt)
        return 0

    def to_command(self, text):
        """Traduit la reconnaissance vocale en commandes"""
        text += " "
        c, i1, i2 = 0, 0, 0
        dig = 0.0
        rot = Rotation_Regex.findall(text)
        snrot = Snclock_Regex.findall(text)
        lin = LIN_Regex.findall(text)
        slin = SLIN_Regex.findall(text)
        if digit_regex.search(text) is not None:
            dig = digit_regex.search(text).group(0)
        if len(rot) != 0 or len(snrot) != 0 or len(Sclock_Regex.findall(text)) !=0:
            c = 0
            # print(snrot)
            if digit_regex.search(text) is not None:
                # print(dig)
                i1 = float(dig)
            else:
                i1 = 90
            if len(snrot) != 0:
                i1 = -i1
        else:  # OR len(lin)!=0
            c = 1
            if digit_regex.search(text) is not None:
                i1 = dig
            else:
                i1 = 1
            if len(slin) != 0:
                i1 = -i1
        command_dict = {0: 'ROT', 1: 'LIN', 2: 'CIR'}
        self.cmdentry.delete(0, tkinter.END)
        if int(c) == 0:
            self.cmdentry.insert(0, "{0}({1})\n".format(command_dict[int(c)], i1))
        elif int(c) == 1:
            self.cmdentry.insert(0, "{0}(d={1})\n".format(command_dict[int(c)], i1))
        return c, i1, i2

    def confirm(self):
        """Soumet la commande"""
        c, i1, i2 = self.v_command
        if c == 0:
            self.ROT(ang_entry=float(i1), entry=True)
        if c == 1:
            self.LIN(d_entry=float(i1), entry=True)
        return 0


Interface()
tkinter.mainloop()
