from numpy import *
import pygame
from math import *
from operator import add
import matplotlib.pyplot as plt

global v_droit
global v_gauche


values = open("values.txt", "r")
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
                theta += delay*time*amax*(1-rapport)/L
            else:
                vitesses_droite.append(abs(rapport) * time * amax / r)
                vitesses_gauche.append(time * amax / r)
                theta += delay * time * amax * (rapport - 1)/L

        for nombre in range(int((d_ext / vmax - tau_plat) / delay) + 1):
            time = nombre * delay
            if dx_veh < 0:  # On tourne a gauche
                vitesses_droite.append(vmax / r)
                vitesses_gauche.append(rapport * vmax / r)
                theta += delay * vmax * (1 - rapport) / L
            else:
                vitesses_droite.append(rapport * vmax / r)
                vitesses_gauche.append(vmax / r)
                theta += delay * vmax *(rapport - 1) / L

        for nombre in range(int(tau_plat / delay)):
            time = nombre * delay
            if dx_veh < 0:  # On tourne a gauche
                vitesses_droite.append(vmax / r - time * amax / r)
                vitesses_gauche.append(vmax * rapport / r - rapport * time * amax / r)
                theta += delay * time * amax * (1 - rapport) / L
            else:
                vitesses_droite.append(vmax / r * rapport - rapport * time * amax / r)
                vitesses_gauche.append(vmax / r - time * amax / r)
                theta += delay * time * amax * (rapport - 1) / L
        return vitesses_droite, vitesses_gauche, tau_plat, theta

    else:

        for nombre in range(int(tau / delay)+1):
            time = nombre * delay
            if dx_veh < 0:  # On tourne a gauche
                # print("gauche")
                vitesses_droite.append(time * amax / r)
                vitesses_gauche.append(rapport * time * amax / r)
                theta += delay * time * amax * (1 - rapport) /L
            else:
                vitesses_droite.append(rapport * time * amax / r)
                vitesses_gauche.append(time * amax / r)
                theta += delay * time * amax * (rapport - 1) / L

        for nombre in range(int(tau / delay)+1):
            time = nombre * delay
            if dx_veh < 0:  # On tourne a gauche
                vitesses_droite.append(amax * tau / r - time * amax / r)
                vitesses_gauche.append(rapport * (amax * tau / r - time * amax / r))
                theta += delay * amax * (tau - time) * (1 - rapport) / L
            else:
                vitesses_droite.append(rapport * (amax * tau / r - time * amax / r))
                vitesses_gauche.append(amax * tau / r - time * amax / r)
                theta += delay * amax * (tau - time) * (rapport - 1) / L
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
    global commande_p

    vitesses_mot_droit = []
    vitesses_mot_gauche = []

    ### INITIALISATION ###
    for commandes in ordres:
        commande=commandes[0]
        if commande == "L":
            distance = float(commandes.split(",")[1])
            v_droit, v_gauche, tau_p = ligne_theo(distance)
            x += distance * cos(theta)
            y += distance * sin(theta)

        elif commande == "R":
            angle = float(commandes.split(",")[1])
            v_droit, v_gauche, tau_p = rot_theo(angle)
            theta += angle

        elif commande == "A":
            xc = float(commandes.split(",")[1])
            yc = float(commandes.split(",")[2])
            v_droit, v_gauche, tau_p, theta = arc_theo(x, y, theta, xc, yc)
            x, y = xc, yc

        vitesses_mot_droit=vitesses_mot_droit+v_droit
        vitesses_mot_gauche=vitesses_mot_gauche+v_gauche

    return vitesses_mot_droit, vitesses_mot_gauche


main()

