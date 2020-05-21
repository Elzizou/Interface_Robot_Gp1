import matplotlib.pyplot as plt
import numpy as np
import math
import tkinter
import os
import matplotlib.patches as mpatches
from vocal.speech_reco_tk import Srwindow
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import tkinter.scrolledtext as tkscrolledtext

class Interface():
    # VARIABLES
    FIGSIZE = (5, 4)
    DPI = 100
    DRAW_METHOD = 1 #Permet à l'interface de choisir entre les méthodes de tracé (LIN,CIR)
    AXIS = [-10, 10, -10, 10] #Définit l'espace de travail du robot
    GRID = True # Définit la présence ou non de la grille

    def __init__(self):
        ## Initialisation de Tkinter
        self.root = tkinter.Tk()
        self.root.wm_title("Interface Commande Robot")

        self.setup()
        # Variables
        self.init_graph()

        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        self.canvas.mpl_connect("button_press_event", self.on_key_press)
        self.textbox = tkscrolledtext.ScrolledText(master=self.root, wrap='word', height=2)
        self.textbox.pack(side=tkinter.TOP, fill='x', expand=1)
        self.set_buttons()

    def setup(self):
        """Mise en place de la Figure Matplotlib"""
        self.fig = Figure(figsize=self.FIGSIZE, dpi=self.DPI)
        self.ax = self.fig.add_subplot(111)
        self.ax.axis(self.AXIS)

        self.set_grid()

        self.robot_im = plt.imread('robot.png')
        self.imgplot = self.ax.imshow(self.robot_im, origin=(0, 0), extent=([-1, 1, -1, 1]))

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.root)
        self.toolbar.update()

    def set_grid(self):
        """Mise en place de la grille"""
        if self.GRID:
            # Major ticks, minor ticks every
            major_ticks = np.arange(self.AXIS[0], self.AXIS[1], 1)
            # minor_ticks = np.arange(-10, 11, 0.5)

            self.ax.set_xticks(major_ticks)
            # self.ax.set_xticks(minor_ticks, minor=True)
            self.ax.set_yticks(major_ticks)
            # self.ax.set_yticks(minor_ticks, minor=True)

            # And a corresponding grid
            self.ax.grid(which='both', alpha=0.2)
            self.ax.set_axisbelow(True)

    def set_buttons(self):
        """Mise en place des boutons sur Tkinter"""
        self.query_frame = tkinter.Frame(self.root)
        # Create new window to add entries by hand
        self.window_button = tkinter.Button(self.query_frame, text="Command Window", command=self.create_window)
        self.window_button.pack(side=tkinter.LEFT)

        self.update_linmethodbutton = tkinter.Button(master=self.query_frame, text="Line",
                                                     command=self.to_Line, relief=tkinter.SUNKEN)
        self.update_linmethodbutton.pack(side=tkinter.LEFT)

        self.update_cirmethodbutton = tkinter.Button(master=self.query_frame, text="CIR",
                                                     command=self.to_CIR)
        self.update_cirmethodbutton.pack(side=tkinter.LEFT)

        self.erase_methodbutton = tkinter.Button(master=self.query_frame, text="Erase",
                                                 command=self.erase_plt)
        self.erase_methodbutton.pack(side=tkinter.LEFT)

        self.pos_button = tkinter.Button(master=self.query_frame, text="Simulation", command=self.Simulation)
        self.pos_button.pack(side=tkinter.LEFT)

        self.export_button = tkinter.Button(master=self.query_frame, text="Export", command=self.command_txt)
        self.export_button.pack(side=tkinter.LEFT)

        self.mic_button = tkinter.Button(master=self.query_frame, text="Mic", command=self.mic)
        self.mic_button.pack(side=tkinter.LEFT)

        self.query_frame.pack(side = tkinter.LEFT)

        self.quit_button = tkinter.Button(master=self.root, text="Quit", command=self._quit)
        self.quit_button.pack(side=tkinter.BOTTOM)

    def init_graph(self):
        """Initialise la courbe de la trajectoire, ainsi que les commandes et les directions"""
        self.plt_draw = np.zeros((1, 2))  # Coordonnées interprété par matplotlib pour le tracé
        # self.plt_draw[0] = np.array([0, 1])
        self.command = np.zeros((1, 3))
        # self.command[0] = np.array([1, 0, 1])
        self.directions = np.array([[0, 1]])
        self.drawing, = self.ax.plot(self.plt_draw[:, 0], self.plt_draw[:, 1])

    def erase_plt(self):
        """Réinitialise le tracé"""
        self.ax.cla()
        self.init_graph()
        self.textbox.delete('1.0', tkinter.END)
        self.ax.axis(self.AXIS)
        self.set_grid()
        self.robot_im = plt.imread('robot.png')
        self.imgplot = self.ax.imshow(self.robot_im, origin=(0, 1), extent=([-1, 1, -1, 1]))
        self.ax.figure.canvas.draw()

    def on_key_press(self, event):
        """Gestion de l'évènement clic gauche et gestion du tracé"""
        # print("you pressed ({0},{1})".format(event.xdata, event.ydata))
        key_press_handler(event, self.canvas, self.toolbar)
        if event.inaxes != self.ax.axes: return
        x, y = event.xdata, event.ydata
        if np.abs(x) > 10 or np.abs(y) > 10: return
        if self.DRAW_METHOD == 1:  # Ligne droite
            self.draw_lineinter(x, y)
        if self.DRAW_METHOD == 2:  # CIR
            self.draw_CIR(x, y)
        # Update Canvas
        self.drawing.set_data(self.plt_draw[:, 0], self.plt_draw[:, 1])
        self.ax.figure.canvas.draw()

    # Changement de méthode de tracé
    def to_CIR(self):
        """Change la méthode de tracé au CIR"""
        self.update_cirmethodbutton.config(relief=tkinter.SUNKEN)
        self.update_linmethodbutton.configure(relief=tkinter.RAISED)
        self.DRAW_METHOD = 2

    def to_Line(self):
        """Change la méthode de tracé au LIN"""
        self.update_linmethodbutton.config(relief=tkinter.SUNKEN)
        self.update_cirmethodbutton.configure(relief=tkinter.RAISED)
        self.DRAW_METHOD = 1

    def Simulation(self):
        print("Simulation à implanter dans l'interface graphique?")

    # Méthodes de tracé
    def ROT(self):
        """Méthode de Rotation de la voiture"""
        # Update direction
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
        self.ax.figure.canvas.draw()
        return 0

    def LIN(self):
        """Méthode de ligne droite de la voiture"""
        d = float(self.dentry.get())
        xold, yold = self.plt_draw[-1]
        xdir, ydir = self.directions[-1]
        # print("(xold = {0}, yold = {1}, xdir = {2}, ydir = {3}".format(xold, yold, xdir, ydir))
        if d > 0:
            xout = xold + d * xdir
            yout = yold + d * ydir
        else:
            xout = xold + d * xdir
            yout = yold + d * ydir
            self.add_direction(np.array([-self.directions[-1][0], -self.directions[-1][1]]))
        self.plt_draw = np.vstack((self.plt_draw, np.array([xout, yout])))
        self.drawing.set_data(self.plt_draw[:, 0], self.plt_draw[:, 1])
        self.add_command(1, d, 0)
        self.ax.figure.canvas.draw()
        return 0

    def CIR(self):
        """Méthode tracé d'arc de la voiture"""
        self.draw_CIR(float(self.xcirentry.get()), float(self.ycirentry.get()))

    def draw_lineinter(self, x, y):
        """Trace le LIN de la voiture"""
        dv = x - self.plt_draw[-1][0], y - self.plt_draw[-1][1]
        angle = self.get_ang(self.plt_draw[-1], np.array([x, y]), dir=True,
                             direction=self.directions[-1])  # Détermination de l'angle de rotation (valeur absolue)
        self.add_direction(dv)
        # Ajout des coordonnées du click
        self.plt_draw = np.vstack((self.plt_draw, np.array([x, y])))
        # Ajout des commandes
        if np.abs(angle) > 0.001:  # Ajoute une commande de rotation s'il est non nul
            self.add_command(0, angle, 0)
        self.add_command(1, np.linalg.norm(dv), 0)

    def draw_CIR(self, xout, yout):
        """Trace le CIR"""
        xin, yin = self.plt_draw[-1][0], self.plt_draw[-1][1]
        Xcv, Ycv, sgn, X, Y = self.init_arc(xout, yout)
        ang_b = self.get_ang((0, 1), (self.directions[-1][0], self.directions[-1][1]))
        if Xcv==None:
            print("Invalid CIR Command")
            return
        ### Changement de base du cas précédent pour le mettre en modèle global
        dir_2 = self.directions[-1]
        Xn, Yn = list(), list()
        Vn = list()
        for k in range(len(X)):
            xglob, yglob = self.changement_base(X[k], Y[k], ang_b, xin, yin)
            Xn.append(xglob)
            Yn.append(yglob)
            if not np.isnan(xglob) and not np.isnan(yglob):
                Vn.append([xglob,yglob])
        # print(Xn)
        # self.ax.plot(Xn, Yn)
        Vn = np.reshape(np.array(Vn), (len(Vn), 2))
        self.plt_draw = np.vstack((self.plt_draw, np.array(Vn)))
        dv_dir = Xn[-1] - Xn[-2], Yn[-1] - Yn[-2]
        # print(dv_dir)
        self.add_direction(dv_dir)
        self.drawing.set_data(self.plt_draw[:, 0], self.plt_draw[:, 1])
        self.ax.figure.canvas.draw()
        self.add_command(2, xout, yout)

    def init_arc(self, xout, yout):
        """Crée un arc dans la base de la voiture"""
        xin, yin = self.plt_draw[-1][0], self.plt_draw[-1][1]
        ### Calcul dans le cas (x0,y0)=(0,0) et direction = (0,1)
        dx, dy = xout - xin, yout - yin
        xdir, ydir = self.directions[-1][0], self.directions[-1][1]
        ang_b = self.get_ang((1, 0), (self.directions[-1][0], self.directions[-1][1]))
        dxr, dyr = self.rot_inv(xin,yin, xout, yout, np.pi/2-ang_b)
        theta_ini = 0

        Xcv = dyr * np.sin(theta_ini) + dxr * np.cos(theta_ini)
        Ycv = dyr * np.cos(theta_ini) - dxr * np.sin(theta_ini)
        # print("init_arc : Xcv = {0}, Ycv={1}".format(Xcv,Ycv))
        if Ycv < 0: return None, None,None, None, None # On bannit le cas où Ycv<0
        sgn = (Xcv / np.abs(Xcv))
        R = sgn * (Xcv ** 2 + Ycv ** 2) / (2 * Xcv)
        X = np.linspace(0, Xcv, 100)
        Y = np.sqrt(R ** 2 - np.power(X - sgn * R, 2))
        return Xcv, Ycv, sgn, X, Y

    def rot_inv(self, xin, yin, xout, yout, theta):
        dx, dy = xout - xin, yout - yin
        # print("rot_inv : dx = {0}, dy={1}".format(dx,dy))
        # print("rot_inv : theta={}".format(theta))
        dxr, dyr = -np.sin(theta)*dy+np.cos(theta)*dx, np.cos(theta)*dy+np.sin(theta)*dx
        # print("rot_inv : dxr = {0}, dyr={1}".format(dxr,dyr))
        return dxr, dyr

    def changement_base(self, xrel, yrel, theta, x0, y0):
        """Change la base (rotation, translation)"""
        chg_base = np.array([[np.cos(theta), -np.sin(theta), x0],
                             [np.sin(theta), np.cos(theta), y0],
                             [0,0,1]])
        j = np.array([[xrel],
                      [yrel],
                      [1]])
        result = np.dot(chg_base, j)
        return float(result[0]), float(result[1])

    # Méthodes géométriques
    def rotatenp(self, x, y, ang):
        """Use numpy to build a rotation matrix and take the dot product."""
        co, si = np.cos(ang), np.sin(ang)
        j = np.array([[co, si], [-si, co]])
        m = np.dot(j, [x, y])
        return float(m[0]), float(m[1])

    def get_ang(self, v1, v2, dir=False, direction=(0, 1)):
        """Détermine l'angle de rotation avec considération possible de la direction précédante"""
        vect1 = np.array([float(v1[0]), float(v1[1])])
        vect2 = np.array([float(v2[0]), float(v2[1])])
        if dir:
            vect2 = vect2 - vect1
            vect1 = np.array([float(direction[0]), float(direction[1])])
        if  np.linalg.norm(vect1)* np.linalg.norm(vect2)==0:
            print("get_ang: Invalid value")
            return 0
        v1_unit = vect1 / np.linalg.norm(vect1)
        v2_unit = vect2 / np.linalg.norm(vect2)
        dot_product = np.dot(v1_unit, v2_unit)
        sgn = v1_unit[0]*v2_unit[1]-v1_unit[1]*v2_unit[0]
        if sgn!=0:
            sgn = sgn/np.abs(sgn)
        else:
            return 0
        return sgn*np.arccos(dot_product)

    # Méthodes de mise à jour des variables
    def add_command(self, c, i1, i2):
        """Met à jour la liste de commandes"""
        self.command = np.vstack((self.command, np.array([c, i1, i2])))
        command_dict = {0: 'ROT', 1: 'LIN', 2: 'CIR'}
        c = command_dict[int(self.command[-1][0])]
        self.textbox.insert('1.0',
                            "{0}({1},{2})\n".format(c, round(self.command[-1][1], 2), round(self.command[-1][2])), 2)

    def add_direction(self, dv):
        """Met à jour la liste de directions"""
        self.directions = np.vstack((self.directions, dv / np.linalg.norm(dv)))

    def command_txt(self):
        """Renvoie les commande sous forme de fichier texte, la suite du programme est géré par la partie Trajectoire"""
        path = os.getcwd()
        text_data = open(path + "\\values.txt", "w")
        command_dict = {0: 'R', 1: 'L', 2: 'A'}
        # print(self.command)
        for instruct in self.command[1:-1]:
            c = command_dict[int(instruct[0])]
            txt = "{0},{1},{2};".format(c, round(instruct[1], 3), round(instruct[2], 3))
            # print("{0},{1},{2};".format(c, round(instruct[1], 3), round(instruct[2], 3)))
            text_data.write(txt)
        instruct = self.command[-1]
        c = command_dict[int(instruct[0])]
        txt = "{0},{1},{2}".format(c, round(instruct[1], 3), round(instruct[2], 3))
        # print("{0},{1},{2};".format(c, round(instruct[1], 3), round(instruct[2], 3)))
        text_data.write(txt)
        text_data.close()
        print("Commandes exportées!")
        return 0

    def _quit(self):
        """Quitte l'interface"""
        self.root.quit()  # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def create_window(self):
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

    def mic(self):
        window = tkinter.Toplevel
        Srwindow(self.root, window)


Interface()
tkinter.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.
