from time import *
from math import *

### Code de la route ###
vmax = 1 #en m/s (en vrai je crois que c'est 0.42, a verifier)
amax = 0.5#en m/s^2 (la ca correspond a la valeur de r et epsmax

### Contraintes techniques ###
wmax = 10.5   #en rad s-1
epsmax = 12.5 #en rad.s-2
r = 0.04      #4cm
L = 0.3       #30cm

### Valeurs caracteristiques ###
tau_plat = vmax / amax

### Variables utiles pour le prgm ###
start = 0.
sleep_time=0.01

def arc(x,y,theta,xc,yc):
    print(atan(-1))
    print(atan(1))
    print(atan(0))
    global dx, dy
    global dx_veh, dy_veh
    global rayon, rapport, tau

    vrobot=open("vrobot_arc","w")

    dx = xc-x
    dy = yc-y

    dx_veh = -cos(theta)*dy + sin(theta)*dx
    dy_veh = sin(theta)*dy + cos(theta)*dx

    print(dx_veh)
    print(dy_veh)

    rayon = abs((dx_veh*dx_veh+dy_veh*dy_veh)/(2*dx_veh))
    rapport = (2*rayon - L)/(2*rayon +L)
    print(rapport)

    if (dy_veh > 0):
        if abs(dx_veh) == rayon:
            d_ext = (rayon + L / 2) * pi / 2
        elif 0 < abs(dx_veh) < rayon:
            d_ext = (rayon + L / 2) * atan(dy_veh / (rayon - abs(dx_veh)))
        elif abs(dx_veh) > rayon:
            d_ext = (rayon + L / 2) * (pi + atan(dy_veh / (rayon - abs(dx_veh))))
        else:
            d_ext=0
    elif dy_veh<0:
        if abs(dx_veh) == rayon:
            d_ext = (rayon + L / 2) * 3 * pi / 2
        elif 0 < abs(dx_veh) < rayon:
            d_ext = (rayon + L / 2) * (2*pi+atan(dy_veh / (rayon - abs(dx_veh))))
        elif abs(dx_veh) > rayon:
            d_ext = (rayon + L / 2) * (pi + atan(dy_veh / (rayon - abs(dx_veh))))
        else:
            d_ext=0
    else:
        d_ext = (rayon + L / 2) * pi

    tau = sqrt(d_ext/amax)
    print("########################")
    print(d_ext)
    print(tau)
    print(vmax*vmax/amax)
    print(tau_plat)

    #essai.write(str(rayon) + " ; " + str(rapport) + " ; " + str(d_ext))

    ### IL Y A UN PLATEAU ###
    if d_ext >= vmax*vmax/amax:
        #print("plateau")
        start = time()

        while time() - start < tau_plat:
            if dx_veh < 0: #On tourne a gauche
                #print("gauche")
                vrobot.write(str((time()-start)*amax/r) + ",")
                vrobot.write(str(abs(rapport)*(time()-start)*amax/r) + ";")
                sleep(sleep_time)
            else:
                #print("droite")
                vrobot.write(str(abs(rapport)*(time() - start) * amax/r) + ",")
                vrobot.write(str((time() - start) * amax/r) + ";")
                sleep(sleep_time)

        start = time()
        i=0
        while time()-start < d_ext/vmax - tau_plat:
            if dx_veh < 0:  # On tourne a gauche
                vrobot.write(str(vmax/r) + ",")
                vrobot.write(str(rapport * vmax/r) + ";")
                sleep(sleep_time)
            else:
                vrobot.write(str(rapport * vmax/r) + ",")
                vrobot.write(str(vmax/r) + ";")
                sleep(sleep_time)
                print(i)
                i += 1

        start = time()

        while time() - start < tau_plat:
            if dx_veh < 0:  # On tourne a gauche
                vrobot.write(str(vmax/r - (time() - start) * amax/r) + ",")
                vrobot.write(str(vmax*rapport/r - rapport * (time() - start) * amax/r) + ";")
                sleep(sleep_time)
            else:
                vrobot.write(str(vmax/r * rapport - rapport * (time() - start) * amax/r) + ",")
                vrobot.write(str(vmax/r - (time() - start) * amax/r) + ";")
                sleep(sleep_time)
        vrobot.write("0,")
        vrobot.write("0")

        return 0


    ### IL N'Y A PAS DE PLATEAU
    else:

        start = time()
        #print("pas plateau")
        while time() - start < tau:
            if dx_veh < 0: #On tourne a gauche
                print("gauche")
                vrobot.write(str((time()-start)*amax/r)+ ",")
                vrobot.write(str(rapport*(time()-start)*amax/r)+";")
                sleep(sleep_time)
            else:
                #print("droite")
                vrobot.write(str(rapport * (time() - start) * amax/r) + ",")
                vrobot.write(str((time() - start) * amax/r) + ";")
                sleep(sleep_time)

        start = time()

        while time() - start < tau:
            if dx_veh < 0:  # On tourne a gauche
                vrobot.write(str(amax*tau/r - (time() - start) * amax/r) + ",")
                vrobot.write(str(rapport*(amax*tau/r - (time() - start) * amax/r)) + ";")
                sleep(sleep_time)
            else:
                vrobot.write(str(rapport * (amax * tau/r - (time() - start) * amax/r)) + ",")
                vrobot.write(str(amax * tau/r - (time() - start) * amax/r) + ";")
                sleep(sleep_time)
        vrobot.write("0,")
        vrobot.write("0")

        return 0


arc(1,1,pi/4,3,5)
