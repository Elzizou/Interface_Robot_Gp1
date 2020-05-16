from numpy import *
import pygame
from math import *
from operator import add
import matplotlib.pyplot as plt

global v_droit
global v_gauche


values = open("values", "r")
ordres = values.readline().split(";")
v_droit = []
v_gauche = []

delay = 0.01
tau_p = 0.
tau_f = 0.

future_droit = []
future_gauche = []

#********************************************************************************************************************#

                                #### GENERATION DE TRAJECTOIRE BASIQUES ####

def ligne_theo(distance):
    vitesses_droite = []
    vitesses_gauche = []
    tau = vmax / amax
    if distance > vmax * vmax / amax:
        plat = True
        t_plat = distance / vmax - vmax / amax
    else:
        plat = False
        tau2 = sqrt(distance / amax)

    if plat:
        for nombre in range(int(tau / delay)):
            time = nombre * delay
            vitesses_droite.append(amax * time / r)
            vitesses_gauche.append(amax * time / r)
        for nombre in range(int(t_plat / delay)):
            time = nombre * delay
            vitesses_droite.append(vmax / r)
            vitesses_gauche.append(vmax / r)
        for nombre in range(int(tau / delay)):
            time = nombre * delay
            vitesses_droite.append(vmax / r - amax * time / r)
            vitesses_gauche.append(vmax / r - amax * time / r)
        return vitesses_droite, vitesses_gauche, tau
    else:
        for nombre in range(int(tau2 / delay)):
            time = nombre * delay
            vitesses_droite.append(amax * time / r)
            vitesses_gauche.append(amax * time / r)
        for nombre in range(int(tau2 / delay)):
            time = nombre * delay
            vitesses_droite.append(amax * (tau2 - time) / r)
            vitesses_gauche.append(amax * (tau2 - time) / r)
        return vitesses_droite, vitesses_gauche, tau2


def rot_theo(angle):
    vitesses_droite = []
    vitesses_gauche = []

    tau_plat = wmax / epsmax
    tau = sqrt(L * abs(angle) / (2 * r * epsmax))
    tau2 = (abs(angle) - 2 * r * epsmax * tau_plat * tau_plat / L) / wmax * L / 2 / r
    signe = sign(angle)
    #print(signe)
    if abs(angle) < 2 * r * epsmax * tau_plat * tau_plat / L:
        for nombre in range(int(tau / delay) + 1):
            time = nombre * delay
            vitesses_droite.append(signe * time * epsmax)
            vitesses_gauche.append((-1) * signe * time * epsmax)

        for nombre in range(int(tau / delay) + 1):
            time = nombre * delay
            vitesses_droite.append(signe * (tau - time) * epsmax)
            vitesses_gauche.append((-1) * signe * (tau - time) * epsmax)
        return vitesses_droite, vitesses_gauche, tau

    else:
        for nombre in range(int(tau_plat / delay)):
            time = nombre * delay
            vitesses_droite.append(signe * time * epsmax)
            vitesses_gauche.append((-1) * signe * time * epsmax)

        for nombre in range(int(tau2 / delay)):
            time = nombre * delay
            vitesses_droite.append(signe * wmax)
            vitesses_gauche.append((-1) * signe * wmax)

        for nombre in range(int(tau_plat / delay) + 1):
            time = nombre * delay
            vitesses_droite.append(signe * (tau_plat - time) * epsmax)
            vitesses_gauche.append((-1) * signe * (tau_plat - time) * epsmax)
        return vitesses_droite, vitesses_gauche, tau_plat

def arc_theo(x, y, theta, xc, yc):
    vitesses_droite = []
    vitesses_gauche = []

    dx = xc - x
    dy = yc - y

    dx_veh = -cos(theta) * dy + sin(theta) * dx
    dy_veh = sin(theta) * dy + cos(theta) * dx

    rayon = abs((dx_veh * dx_veh + dy_veh * dy_veh) / (2 * dx_veh))
    rapport = (2 * rayon - L) / (2 * rayon + L)

    if (dy_veh > 0):
        if abs(dx_veh) == rayon:
            d_ext = (rayon + L / 2) * pi / 2
        elif 0 < abs(dx_veh) < rayon:
            d_ext = (rayon + L / 2) * atan(dy_veh / (rayon - abs(dx_veh)))
        elif abs(dx_veh) > rayon:
            d_ext = (rayon + L / 2) * (pi + atan(dy_veh / (rayon - abs(dx_veh))))
        else:
            d_ext = 0
    elif dy_veh < 0:
        if abs(dx_veh) == rayon:
            d_ext = (rayon + L / 2) * 3 * pi / 2
        elif 0 < abs(dx_veh) < rayon:
            d_ext = (rayon + L / 2) * (2 * pi + atan(dy_veh / (rayon - abs(dx_veh))))
        elif abs(dx_veh) > rayon:
            d_ext = (rayon + L / 2) * (pi + atan(dy_veh / (rayon - abs(dx_veh))))
        else:
            d_ext = 0
    else:
        d_ext = (rayon + L / 2) * pi

    #print("d_ext = ", d_ext)
    tau_plat = vmax / amax
    tau = sqrt(d_ext / amax)
    #print("tau = ", tau)

    if d_ext >= vmax * vmax / amax:
        for nombre in range(int(tau_plat / delay)):
            time = nombre * delay
            if dx_veh < 0:  # On tourne a gauche
                vitesses_droite.append((time * amax / r))
                vitesses_gauche.append(abs(rapport) * time * amax / r)
                theta += delay*time*amax/r * (1-rapport)/2
            else:
                vitesses_droite.append(abs(rapport) * time * amax / r)
                vitesses_gauche.append(time * amax / r)
                theta += delay * time * amax / r * (rapport - 1) / 2

        for nombre in range(int((d_ext / vmax - tau_plat) / delay) + 1):
            time = nombre * delay
            if dx_veh < 0:  # On tourne a gauche
                vitesses_droite.append(vmax / r)
                vitesses_gauche.append(rapport * vmax / r)
                theta += delay * time * amax / r * (1 - rapport) / 2
            else:
                vitesses_droite.append(rapport * vmax / r)
                vitesses_gauche.append(vmax / r)
                theta += delay * time * amax / r * (rapport - 1) / 2

        for nombre in range(int(tau_plat / delay)):
            time = nombre * delay
            if dx_veh < 0:  # On tourne a gauche
                vitesses_droite.append(vmax / r - time * amax / r)
                vitesses_gauche.append(vmax * rapport / r - rapport * time * amax / r)
                theta += delay * time * amax / r * (1 - rapport) / 2
            else:
                vitesses_droite.append(vmax / r * rapport - rapport * time * amax / r)
                vitesses_gauche.append(vmax / r - time * amax / r)
                theta += delay * time * amax / r * (rapport - 1) / 2
        return vitesses_droite, vitesses_gauche, tau_plat, theta

    else:

        for nombre in range(int(tau / delay) + 1):
            time = nombre * delay
            if dx_veh < 0:  # On tourne a gauche
                # print("gauche")
                vitesses_droite.append(time * amax / r)
                vitesses_gauche.append(rapport * time * amax / r)
                theta += delay * time * amax / r * (1 - rapport) / 2
            else:
                vitesses_droite.append(rapport * time * amax / r)
                vitesses_gauche.append(time * amax / r)
                theta += delay * time * amax / r * (rapport - 1) / 2

        for nombre in range(int(tau_plat / delay)):
            time = nombre * delay
            if dx_veh < 0:  # On tourne a gauche
                vitesses_droite.append(amax * tau / r - time * amax / r)
                vitesses_gauche.append(rapport * (amax * tau / r - time * amax / r))
                theta += delay * time * amax / r * (1 - rapport) / 2
            else:
                vitesses_droite.append(rapport * (amax * tau / r - time * amax / r))
                vitesses_gauche.append(amax * tau / r - time * amax / r)
                theta += delay * time * amax / r * (rapport - 1) / 2
        return vitesses_droite, vitesses_gauche, tau, theta

#********************************************************************************************************************#


def main():
    global delay
    delay = 0.01  # 10 ms
    x, y, theta = 0, 0, pi / 2
    #xp, yp, vp1, vp2 = 0, 0, 0, 0
    global vmax
    vmax = 1
    global amax
    amax = 0.5
    global wmax
    wmax = 10.5
    global epsmax
    epsmax = 12.5
    global L
    L = 0.3  # ecart entre les roues
    global r
    r = 0.04  # rayon de la roue


                                             ### INITIALISATION ###
    #print("initialisation")
    commande = ordres[0].split(",")[0]
    if commande == "L":
        distance = float(ordres[0].split(",")[1])
        v_droit, v_gauche, tau_p = ligne_theo(distance)
        x += distance * cos(theta)
        y += distance * sin(theta)

    elif commande == "R":
        angle = float(ordres[0].split(",")[1])
        v_droit, v_gauche, tau_p = rot_theo(angle)
        theta += angle

    elif commande == "A":
        xc = float(ordres[0].split(",")[1])
        yc = float(ordres[0].split(",")[2])
        v_droit, v_gauche, tau_p, theta = arc_theo(x, y, theta, xc, yc)
        x, y = xc, yc

                                             ### SUPERPOSITION ###

    for compteur in range(len(ordres) - 1):
        #print("tour ", compteur)
        commande = ordres[compteur+1].split(",")[0]
        if commande == "L":
            distance = float(ordres[compteur+1].split(",")[1])
            future_droit, future_gauche, tau_f = ligne_theo(distance)
            x += distance*cos(theta)
            y += distance*sin(theta)

        elif commande == "R":
            angle = float(ordres[compteur+1].split(",")[1])
            future_droit, future_gauche, tau_f = rot_theo(angle)
            theta += angle

        elif commande == "A":
            xc = float(ordres[compteur+1].split(",")[1])
            yc = float(ordres[compteur+1].split(",")[2])
            future_droit, future_gauche, tau_f, theta = arc_theo(x, y, theta, xc, yc)
            x = xc
            y = yc

        else:
            return

        if tau_p >= tau_f:
            v_droit = v_droit[0:len(v_droit)-int(tau_f/delay)] + list(map(add, v_droit[len(v_droit)-1 - int(tau_f/delay):], future_droit[0:int(tau_f/delay)]))
            v_gauche = v_gauche[0:len(v_gauche) - int(tau_f / delay)] + list(map(add, v_gauche[len(v_gauche) - 1 - int(tau_f / delay):], future_gauche[0:int(tau_f / delay)]))
        else:
            v_droit = v_droit[0:len(v_droit)-int(tau_p/delay)] + list(map(add, v_droit[len(v_droit)-int(tau_p/delay):], future_droit[0:int(tau_p/delay)]))
            v_gauche = v_gauche[0:len(v_gauche) - int(tau_p / delay)] + list(map(add, v_gauche[len(v_gauche) - int(tau_p / delay):], future_gauche[0:int(tau_p / delay)]))

        v_droit = v_droit + future_droit[int(tau_f/delay):]
        v_gauche = v_gauche + future_gauche[int(tau_f / delay):]

        tau_p = tau_f

    v_droit.append(0.)
    v_gauche.append(0.)

    print("(x,y) = (", x, ", ", y, ")")
    print("theta (en degrés)= ", (theta%(2*pi))*180/pi)
    temps = [k*delay for k in range(len(v_droit))]
    plt.plot(temps, v_droit, label="v_droit")
    plt.plot(temps, v_gauche, label="vgauche")
    plt.legend()
    plt.show()

main()

