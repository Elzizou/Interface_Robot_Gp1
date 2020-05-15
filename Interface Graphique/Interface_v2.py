import matplotlib.pyplot as plt
import numpy as np
import math
import tkinter
import os
import matplotlib.patches as mpatches

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import tkinter.scrolledtext as tkscrolledtext
from circlefrompt import circles_from_p1p2r


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

        # Create new window to add entries by hand
        self.window_button = tkinter.Button(self.root, text="Command Window", command=self.create_window)
        self.window_button.pack(side=tkinter.LEFT)

        self.update_linmethodbutton = tkinter.Button(master=self.root, text="Line",
                                                     command=self.to_Line, relief=tkinter.SUNKEN)
        self.update_linmethodbutton.pack(side=tkinter.LEFT)

        self.update_cirmethodbutton = tkinter.Button(master=self.root, text="CIR",
                                                     command=self.to_CIR)
        self.update_cirmethodbutton.pack(side=tkinter.LEFT)

        self.erase_methodbutton = tkinter.Button(master=self.root, text="Erase",
                                                 command=self.erase_plt)
        self.erase_methodbutton.pack(side=tkinter.LEFT)

        self.pos_button = tkinter.Button(master=self.root, text="Pos", command=self.pos_meth)
        self.pos_button.pack(side=tkinter.LEFT)

        self.command_button = tkinter.Button(master=self.root, text="Command", command=self.print_command)
        self.command_button.pack(side=tkinter.LEFT)

        self.export_button = tkinter.Button(master=self.root, text="Export", command=self.command_txt)
        self.export_button.pack(side=tkinter.LEFT)

        self.dir_button = tkinter.Button(master=self.root, text="dir", command=self.print_dir)
        self.dir_button.pack(side=tkinter.LEFT)

        self.dirtest_button = tkinter.Button(master=self.root, text="arrow dir", command=self.test_dir)
        self.dirtest_button.pack(side=tkinter.LEFT)

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

    def pos_meth(self):
        """Met en place la méthode Position"""
        self.DRAW_METHOD = 3

    def print_dir(self):
        """Affiche la liste des directions sur l'invité de commande"""
        print(self.directions)

    def test_dir(self):
        """Affiche une flèche pour symboliser la direction de la voiture, ainsi que la normale"""
        xold, yold = self.plt_draw[-1]
        xdir, ydir = self.directions[-1]
        self.ax.arrow(xold, yold, xdir, ydir, width=0.2)
        self.ax.arrow(xold, yold, -ydir, xdir, width=0.2, color='g', alpha=0.1)
        self.ax.figure.canvas.draw()

    def to_CIR(self):
        """Change la méthode de tracé au CIR"""
        self.update_cirmethodbutton.config(relief=tkinter.SUNKEN)
        self.update_linmethodbutton.configure(relief=tkinter.RAISED)
        self.DRAW_METHOD = 2

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

    def to_Line(self):
        """Change la méthode de tracé au LIN"""
        self.update_linmethodbutton.config(relief=tkinter.SUNKEN)
        self.update_cirmethodbutton.configure(relief=tkinter.RAISED)
        self.DRAW_METHOD = 1

    def on_key_press(self, event):
        """Gestion de l'évènement clic gauche et gestion du tracé"""
        print("you pressed ({0},{1})".format(event.xdata, event.ydata))
        key_press_handler(event, self.canvas, self.toolbar)
        if event.inaxes != self.ax.axes: return
        x, y = event.xdata, event.ydata
        if np.abs(x) > 10 or np.abs(y) > 10: return
        if self.DRAW_METHOD == 1:  # Ligne droite
            self.draw_lineinter(x, y)
        if self.DRAW_METHOD == 2:  # CIR
            self.draw_CIR(x, y)
        if self.DRAW_METHOD == 3:
            self.test_pos(x, y)
        # Update Canvas
        self.drawing.set_data(self.plt_draw[:, 0], self.plt_draw[:, 1])
        self.ax.figure.canvas.draw()

    def create_window(self):
        """Affiche l'invité de commande LIN,CIR,ROT"""
        self.window = tkinter.Toplevel(self.root)
        self.set_windowbutton()

    def test_pos(self, x, y):
        """Signalise sur l'invité de commande si on clique à gauche ou droite de la voiture"""
        xdir, ydir = self.directions[-1][0], self.directions[-1][1]
        xold, yold = self.plt_draw[-1]
        print(np.dot([-ydir, xdir], [x - xold, y - yold]))
        if np.dot([-ydir, xdir], [x - xold, y - yold]) > 0:
            print("A gauche chef")
        else:
            print("A droite chef")

    def get_ang(self, v1, v2, dir=False, direction=(0, 1)):
        """Détermine l'angle de rotation avec considération possible de la direction précédante"""
        vect1, vect2 = v1, v2
        if dir:
            vect2 = vect2 - vect1
            vect1 = direction
        v1_unit = vect1 / np.linalg.norm(vect1)
        v2_unit = vect2 / np.linalg.norm(vect2)
        dot_product = np.dot(v1_unit, v2_unit)
        return np.arccos(dot_product)

    def ROT(self):
        """Méthode de Rotation de la voiture"""
        # Update direction
        angrad = float(self.thetaentry.get()) * np.pi * 2 / 360
        xdir, ydir = self.directions[-1]
        new_dir = self.rotatenp(xdir, ydir, angrad)
        new_dir = np.array([round(new_dir[0], 2), round(new_dir[1], 2)])
        self.add_direction(new_dir)
        # Add command
        self.add_command(0, angrad, 0)
        # Plot point to show rotation
        x, y = self.plt_draw[-1]
        self.ax.plot(x, y, 'ro', alpha=0.5)
        self.ax.figure.canvas.draw()
        return 0

    def rotatenp(self, x, y, ang):
        """Use numpy to build a rotation matrix and take the dot product."""
        co, si = np.cos(ang), np.sin(ang)
        j = np.array([[co, si], [-si, co]])
        m = np.dot(j, [x, y])
        return float(m[0]), float(m[1])

    def LIN(self):
        """Méthode de ligne droite de la voiture"""
        d = float(self.dentry.get())
        xold, yold = self.plt_draw[-1]
        xdir, ydir = self.directions[-1]
        print("(xold = {0}, yold = {1}, xdir = {2}, ydir = {3}".format(xold, yold, xdir, ydir))
        if d > 0:
            xout = xold + d * xdir
            yout = yold + d * ydir
        else:
            xout = xold + d * xdir
            yout = yold + d * ydir
            self.add_direction(np.array([-self.directions[-1][0], -self.directions[-1][1]]))
        self.plt_draw = np.vstack((self.plt_draw, np.array([xout, yout])))
        self.drawing.set_data(self.plt_draw[:, 0], self.plt_draw[:, 1])
        self.add_command(1, xout, yout)
        self.ax.figure.canvas.draw()
        return 0

    def CIR(self):
        """Méthode tracé d'arc de la voiture"""
        print(self.plt_draw[-1][0], self.plt_draw[-1][1], self.xcirentry.get(), self.ycirentry.get())
        self.draw_CIR(float(self.xcirentry.get()), float(self.ycirentry.get()))
        # self.command = np.vstack((self.command, np.array([2, self.xcirentry.get(), self.ycirentry.get()])))
        self.add_command(2, self.xcirentry.get(), self.ycirentry.get())

    def draw_lineinter(self, x, y):
        """Trace le LIN de la voiture"""
        dv = x - self.plt_draw[-1][0], y - self.plt_draw[-1][1]
        angle = self.get_ang(self.plt_draw[-1], np.array([x, y]), dir=True,
                             direction=self.directions[-1])  # Détermination de l'angle de rotation (valeur absolue)
        self.add_direction(dv)
        # Ajout des coordonnées du click
        self.plt_draw = np.vstack((self.plt_draw, np.array([x, y])))
        if np.dot((self.directions[-1][0], 0),
                  (1, 0)) > 0:  # Essai pour déterminer le signe de l'angle mais infructueux
            angle = -angle
        # Ajout des commandes
        if np.abs(angle) > 0.001:  # Ajoute une commande de rotation s'il est non nul
            self.add_command(0, angle, 0)
        self.add_command(1, x, y)

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

    def init_arc(self, xout, yout):
        """Crée un arc dans la base de la voiture"""
        xin, yin = self.plt_draw[-1][0], self.plt_draw[-1][1]
        ### Calcul dans le cas (x0,y0)=(0,0) et direction = (0,1)
        dx, dy = xout - xin, yout - yin
        self.ax.plot([0,dx], [0,dy],color='r')
        ## TEST print dx, dy absolue
        # theta = self.get_ang((1,0),self.directions[-1])
        theta = np.pi/4
        print("init_arc : theta={}".format(theta))
        dxr, dyr = -np.sin(theta)*dy+np.cos(theta)*dx, np.cos(theta)*dy+np.sin(theta)*dx
        print("dxr = {0}, dyr={1}".format(dxr,dyr))
        # dx,dy=dxr, dyr
        ## Test print dx, dy relatif
        # self.ax.plot([0,dxr], [0,dyr], color='k')
        theta_ini = self.get_ang((1, 0), (1, 0))
        Xcv = dy * np.sin(theta_ini) + dx * np.cos(theta_ini)
        Ycv = dy * np.cos(theta_ini) - dx * np.sin(theta_ini)
        if Ycv < 0: return  # On bannit le cas où Ycv<0
        sgn = (Xcv / np.abs(Xcv))
        R = sgn * (Xcv ** 2 + Ycv ** 2) / (2 * Xcv)
        X = np.linspace(0, Xcv, 100)
        Y = np.sqrt(R ** 2 - np.power(X - sgn * R, 2))
        # self.ax.plot(X, Y)
        return Xcv, Ycv, sgn, X, Y

    def draw_CIR(self, xout, yout):
        """Trace le CIR"""
        xin, yin = self.plt_draw[-1][0], self.plt_draw[-1][1]
        Xcv, Ycv, sgn, X, Y = self.init_arc(xout, yout)

        ### Changement de base du cas précédent pour le mettre en modèle global
        dir_2 = self.directions[-1]
        theta = np.pi/2 - self.get_ang((1,0),dir_2)
        # theta = sgn * np.arctan(Ycv / Xcv)
        print("L'angle est {0}".format(theta))
        Xn, Yn = list(), list()
        for k in range(len(X)):
            xglob, yglob = self.changement_base(X[k], Y[k], theta, xin, yin)
            Xn.append(xglob)
            Yn.append(yglob)
        self.ax.plot(Xn, Yn)
        dv_dir = X[-1][0] - X[-2][0], Y[-1][0] - Y[-2][0]
        print(dv_dir)
        self.add_direction(dv_dir)
        self.drawing.set_data(self.plt_draw[:, 0], self.plt_draw[:, 1])
        self.ax.figure.canvas.draw()
        self.add_command(2, xout, yout)

    def draw_CIR2(self, xout, yout):
        """Trace le CIR, méthode 2"""
        xin, yin = self.plt_draw[-1][0], self.plt_draw[-1][1]
        xdir, ydir = self.directions[-1]
        gauche = np.dot([-ydir, xdir], [xout - xin, yout - yin]) / np.abs(
            np.dot([-ydir, xdir], [xout - xin, yout - yin]))
        if (yout == 0 or xout == 0):
            print("Configuration impossible pour CIR")
        else:
            dx, dy = xout - xin, yout - yin
            theta_ini = self.get_ang((0, 1), (0, 1))
            Xcv = dy * np.sin(theta_ini) + dx * np.cos(theta_ini)
            Ycv = dy * np.cos(theta_ini) - dx * np.sin(theta_ini)
            sgn = (Xcv / np.abs(Xcv))
            R = sgn * (Xcv ** 2 + Ycv ** 2) / (2 * Xcv)
            c1 = circles_from_p1p2r((xin, yin), (xout, yout), R)
            c11, c12 = c1
            xc1, yc1, r1 = c11.x, c11.y, c11.r
            gauchec1 = np.dot([-ydir, xdir], [xc1 - xin, yc1 - yin]) / np.abs(
                np.dot([-ydir, xdir], [xc1 - xin, yc1 - yin]))
            # print("Circle 1 (x={0}, y={1}, r={2}".format(xc1,yc1,r1))
            circle1 = plt.Circle((xc1, yc1), r1, alpha=0.1)
            # self.ax.plot(xc1,yc1,'ro', color='b')

            xc2, yc2, r2 = c12.x, c12.y, c12.r
            gauchec2 = np.dot([-ydir, xdir], [xc2 - xin, yc2 - yin]) / np.abs(
                np.dot([-ydir, xdir], [xc2 - xin, yc2 - yin]))
            # print("Circle 2 (x={0}, y={1}, r={2}".format(xc2,yc2,r2))
            circle2 = plt.Circle((xc2, yc2), r2, alpha=0.1)
            # self.ax.plot(xc2,yc2,'ro', color='g')
            self.ax.add_artist(circle2)
            self.ax.add_artist(circle1)
            X = np.linspace(xin, xout, 101)
            Yp1 = yc1 + np.sqrt(r2 ** 2 - np.power(X - xc1, 2))
            Yn1 = yc1 - np.sqrt(r2 ** 2 - np.power(X - xc1, 2))
            Yp2 = yc2 + np.sqrt(r2 ** 2 - np.power(X - xc2, 2))
            Yn2 = yc2 - np.sqrt(r2 ** 2 - np.power(X - xc2, 2))
            Ytp1 = yc1 + np.sqrt(r2 ** 2 - np.power(X + xc1, 2))
            Ytn1 = yc1 - np.sqrt(r2 ** 2 - np.power(X + xc1, 2))
            Ytp2 = yc2 + np.sqrt(r2 ** 2 - np.power(X + xc2, 2))
            Ytn2 = yc2 - np.sqrt(r2 ** 2 - np.power(X + xc2, 2))
            # length_dict  ={0:self.length(X,Yp1),1:self.length(X,Yn1),2:self.length(X,Yp2),3:self.length(X,Yn2)}
            Y = [Yp1, Yn1, Yp2, Yn2, Ytp1, Ytp2, Ytn1, Ytn2]
            Yt = list()
            length_dict = dict()
            for y_d in Y:
                vtest = X[len(X) // 2], y_d[len(X) // 2]
                sens = (np.dot([xdir, ydir], [vtest[0] - xin, vtest[1] - yin]) /
                        np.abs(np.dot([xdir, ydir], [vtest[0] - xin, vtest[1] - yin])))
                if y_d[-1] * yout and y_d[0] * yin and np.abs(np.abs(y_d[-1]) - np.abs(yout)) < 1e-5 \
                        and np.abs(np.abs(y_d[0]) - np.abs(yin)) < 1e-5 and sens:
                    Yt = [Yt, y_d]
                    length_dict.setdefault(len(Yt), self.length(X, y_d))
            key_min = min(length_dict.keys(), key=(lambda k: length_dict[k]))
            self.ax.plot(X, Y[key_min])
            dv = X[-1] - X[-2], Y[key_min][-1] - Y[key_min][-2]
            self.directions = np.vstack(
                (self.directions, np.array(dv / np.linalg.norm(dv))))
            # if gauche>0 and gauchec2>0: #le point est à gauche de la voiture
            #     print("ggc2")
            #     Y2 = yc2 - np.sqrt(r2**2-np.power(X-xc2,2))
            #     self.ax.plot(X,Y2, color='g')
            #     self.ax.add_artist(circle2)
            #     dv = X[-1]-X[-2], Y2[-1]-Y2[-2]
            #     self.directions = np.vstack(
            #         (self.directions, np.array(dv / np.linalg.norm(dv))))
            # elif gauche<0 and gauchec2<0: #le point est à gauche de la voiture
            #     print("ddc2")
            #     Y2 = yc2 - gauchec2*np.sqrt(r2**2-np.power(X-xc2,2))
            #     self.ax.plot(X,Y2, color='g')
            #     self.ax.add_artist(circle2)
            #     dv = X[-1]-X[-2], Y2[-1]-Y2[-2]
            #     self.directions = np.vstack(
            #         (self.directions, np.array(dv / np.linalg.norm(dv))))
            # elif gauche>0 and gauchec1>0:
            #     Y1 = yc1 - np.sqrt(r1**2-np.power(X-xc1,2))
            #     print("ggc1")
            #     self.ax.plot(X,Y1, color='r')
            #     self.ax.add_artist(circle1)
            #     dv = X[-1]-X[-2], Y1[-1]-Y1[-2]
            #     self.directions = np.vstack(
            #         (self.directions, np.array(dv / np.linalg.norm(dv))))
            # elif gauche<0 and gauchec1<0:
            #     Y1 = yc1 - gauchec1*np.sqrt(r1**2-np.power(X-xc1,2))
            #     print("ddc1")
            #     self.ax.plot(X,Y1, color='r')
            #     self.ax.add_artist(circle1)
            #     dv = X[-1]-X[-2], Y1[-1]-Y1[-2]
            #     self.directions = np.vstack(
            #         (self.directions, np.array(dv / np.linalg.norm(dv))))
            self.plt_draw = np.vstack((self.plt_draw, np.array([xout, yout])))
        return 0

    def length(self, data1, data2):
        """calcule la longueur de la trajectoire"""
        l = 0
        for k in range(1, len(data2)):
            delta = data1[k] - data1[k - 1], data2[k] - data2[k - 1]
            l += np.linalg.norm(delta)
        return l

    def changement_base(self, xrel, yrel, theta, x0, y0):
        """Change la base (rotation, translation)"""
        chg_base = np.array([[np.cos(theta), -np.sin(theta), x0],
                             [np.cos(theta), np.sin(theta), y0],
                             [0,0,1]])
        j = np.array([[xrel],
                      [yrel],
                      [1]])
        result = np.dot(chg_base, j)
        return result[0], result[1]

    def print_command(self):
        """Imprime les commandes sur la console"""
        print(self.command)

    def command_txt(self):
        """Renvoie les commande sous forme de fichier texte, la suite du programme est géré par la partie Trajectoire"""
        path = os.getcwd()
        text_data = open(path + "\\trajectoire.txt", "w")
        for instruct in self.command:
            txt = "{0};{1};{2}\n".format(int(instruct[0]), round(instruct[1], 3), round(instruct[2], 3))
            text_data.write(txt)
        text_data.close()
        return 0

    def _quit(self):
        """Quitte l'interface"""
        self.root.quit()  # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

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


Interface()
tkinter.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.
