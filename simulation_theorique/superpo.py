from numpy import *
from math import *
from operator import add
import matplotlib.pyplot as plt
import os

filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "interface_graphique", "values.txt")
                    #### GENERATION DE TRAJECTOIRE BASIQUES ####

def ligne_theo(distance, theta):
    Vx = []
    Vy = []
    tau = vmax / amax
    if distance > vmax * vmax / amax: #Condition de plateau, pour observer un vrai trapèze
        plat = True
        t_plat = distance / vmax - vmax / amax
    else:                             #Distance pas assez grande pour trapèze avec accélération max, triangle
        plat = False
        tau2 = sqrt(distance / amax)


    if plat:

        for nombre in range(int(tau / delay)): #Pente ascendante
            time = nombre * delay
            Vx.append(cos(theta)*amax*time)
            Vy.append(sin(theta)*amax*time)

        for nombre in range(int(t_plat / delay)): #Plateau
            Vx.append(cos(theta)*vmax)
            Vy.append(sin(theta)*vmax)

        for nombre in range(int(tau / delay)): #Pente descendante
            time = nombre * delay
            Vx.append(cos(theta) * (vmax-amax * time))
            Vy.append(sin(theta) * (vmax-amax * time))

        return Vx, Vy, tau

    else:
        for nombre in range(int(tau2 / delay)): #Pente ascendante
            time = nombre * delay
            Vx.append(cos(theta) * amax * time)
            Vy.append(sin(theta) * amax * time)

        for nombre in range(int(tau2 / delay)): #Pente descendante
            time = nombre * delay
            Vx.append(cos(theta) * amax * (tau2 - time))
            Vy.append(sin(theta) * amax * (tau2 - time))
        return Vx, Vy, tau2

                    #### PROGRAMME PRINCIPAL DE SUPERPOSITION ####


def main():
    values = open(filepath, "r")
    ordres = values.readline().split(";")

    tau_p = 0.
    tau_f = 0.

    global delay
    delay = 0.01  # 10 ms
    x, y, theta = 0, 0, pi / 2
    #xp, yp, vp1, vp2 = 0, 0, 0, 0
    global vmax
    vmax = 1
    global amax
    amax = 0.05
    global wmax
    wmax = 200
    global epsmax
    epsmax = 12.5
    global L
    L = 0.3  # ecart entre les roues
    global r
    r = 0.04  # rayon de la roue
    global commande_p



                             ### INITIALISATION ###
    #print("initialisation")
    commande = ordres[0].split(",")[0]
    if commande == "L":
        distance = float(ordres[0].split(",")[1])
        Lvx, Lvy, tau_p = ligne_theo(distance, theta)

    elif commande == "R":
        angle = float(ordres[0].split(",")[1])
        theta += angle

                                ### SUPERPOSITION ###

    for compteur in range(len(ordres) - 1):

        ### On lit l'idendentifiant de la commande actuelle
        commande = ordres[compteur+1].split(",")[0]

        ###  On l'exécute
        if commande == "L":
            distance = float(ordres[compteur+1].split(",")[1])
            Lvx_f, Lvy_f, tau_f = ligne_theo(distance, theta)

        elif commande == "R":
            angle = float(ordres[compteur+1].split(",")[1])
            theta += angle

        # Si il y a une erreur dans le message, on l'arrête immédiatement
        else:
            return

        ### Si ni la commande actuelle ni la commande suivante ne sont des rotations, on superpose les vitesses
        if (commande != "R"):

            tau_min = min(tau_p, tau_f)

            ###La superposition en elle même
            Lvx = Lvx[0:len(Lvx)-int(tau_min/delay)] + list(map(add, Lvx[(len(Lvx) - int(tau_min/delay)):], Lvx_f[0:int(tau_min/delay)]))
            Lvy = Lvy[0:len(Lvy) - int(tau_min / delay)] + list(map(add, Lvy[(len(Lvy)- int(tau_min / delay)):], Lvy_f[0:int(tau_min / delay)]))

            Lvx = Lvx + Lvx_f[int(tau_min/delay):]
            Lvy = Lvy + Lvy_f[int(tau_min / delay):]

            tau_p = tau_f



    ### Une fois tout cela finit, on rajoute "à la main" 0 à la fin, pour être sûr que le robot s'arrête bien à la fin,
    ### et qu'il ne reste pas une petite valeur de vitesse faisant dériver le robot à l'infini.
    Lvx.append(0.)
    Lvy.append(0.)

    Lw = [0.]
    for k in range(1,len(Lvx)-2):
        Lw.append((atan2(Lvy[k+1], Lvx[k+1])-atan2(Lvy[k], Lvx[k]))/delay)
    Lw.append(0.)
    Lw.append(0.)

    w_droit = []
    w_gauche = []

    for k in range(len(Lvx)-1):
        w_droit.append((sqrt(Lvx[k]**2+Lvy[k]**2)+Lw[k]*L/2)/r)
        w_gauche.append((sqrt(Lvx[k]**2+Lvy[k]**2)-Lw[k]*L/2)/r)

    w_droit.append(0.)
    w_gauche.append(0.)

    print("Lw = ", Lw)
    rap1=[atan2(Lvy[k], Lvx[k])for k in range(len(Lvx))]
    rap2=[atan2(Lvy[k+1], Lvx[k+1])for k in range(len(Lvx)-1)]+[0]

    temps = [k*delay for k in range(len(Lw))]
    plt.plot(temps, Lw, color='blue')
    plt.plot(temps, rap1, color='red')
    plt.plot(temps, rap2, color='red')
    plt.show()


    return w_droit, w_gauche

if __name__=="__main__":
    filepath = "values.txt"
    main()
