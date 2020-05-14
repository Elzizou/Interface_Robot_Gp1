from time import *
from math import *

### Contraintes techniques
vmax=1
amax=0.5
wmax = 10.5   #en rad s-1
epsmax = 12.5 #en rad.s-2
r = 0.04      #4cm
L = 0.3       #30cm
#wmax=vmax/r
#epsmax=amax/r

start = 0

### ATTENTION angle en radian, ou sinon le convertir mais il faut etre coherent ###


def rotation(angle):
    global tau_plat
    global tau
    vrobot = open("vrobot_rot", "w")

    tau_plat = wmax/epsmax
    tau = sqrt(L*abs(angle)/(2*r*epsmax))


    ###IL N'Y A PAS DE PLATEAU
    if abs(angle) < 2*r*epsmax*tau_plat*tau_plat/L:

        start = time()

        ### SI ON PIVOTE VERS LA GAUCHE ###
        if angle >= 0:
            #print("a")

            while time() - start < tau:
                vrobot.write(str((time()-start)*epsmax) + ",")
                vrobot.write(str(-(time() - start) * epsmax) + ";")
                sleep(0.01)
            #vrobot.write("\n")
            #vrobot.write("\n")

            start = time()

            while time()- start < tau:
                vrobot.write(str((tau - (time()-start))*epsmax) + ",")
                vrobot.write(str(-(tau - (time()-start))*epsmax) + ";")
                sleep(0.01)
            vrobot.write(str(0) + ",")
            vrobot.write(str(0))

            return 0

        ###SI ON PIVOTE VERS LA DROITE
        else:
            #print("b")
            while time() - start < tau:
                vrobot.write(str(-(time() - start) * epsmax) + ",")
                vrobot.write(str((time() - start) * epsmax) + ";")
                sleep(0.01)
            #vrobot.write("\n")
            #vrobot.write("\n")

            start = time()

            while time() - start < tau:
                vrobot.write(str(-(tau - (time() - start)) * epsmax) + ",")
                vrobot.write(str((tau - (time() - start)) * epsmax) + ";")
                sleep(0.01)
            vrobot.write(str(0) + ",")
            vrobot.write(str(0))

            return 0



    ### IL Y A UN PLATEAU
    else:

        start = time()

        ### SI ON PIVOTE VERS LA GAUCHE ###
        if angle >= 0:
            #print("c")
            while time() - start < tau_plat:
                vrobot.write(str((time() - start) * epsmax) + ",")
                vrobot.write(str(-(time() - start) * epsmax) + ";")
                sleep(0.01)
            #vrobot.write("\n")
            #vrobot.write("\n")

            start = time()

            while time() - start < (abs(angle) - 2*r*epsmax*tau_plat*tau_plat/L)/wmax*L/2/r:
                vrobot.write(str(wmax) + ",")
                vrobot.write(str(-wmax) + ";")
                sleep(0.01)
            #vrobot.write("\n")
            #vrobot.write("\n")

            start = time()

            while time() - start < tau_plat:
                vrobot.write(str(wmax-(time()-start)*epsmax) + ",")
                vrobot.write(str(-wmax+(time()-start)*epsmax) + ";")
                sleep(0.01)
            vrobot.write(str(0) + ",")
            vrobot.write(str(0))

            return 0

        ### SI ON PIVOTE VERS LA DROITE ###
        else:
            #print("d")
            while time() - start < tau_plat:
                vrobot.write(str(-(time() - start) * epsmax) + ",")
                vrobot.write(str((time() - start) * epsmax) + ";")
                sleep(0.01)
            #vrobot.write("\n")
            #vrobot.write("\n")

            start = time()

            while time() - start < (abs(angle) - 2 * r * epsmax * tau_plat * tau_plat / L)/wmax*L/2/r:
                #print("f")
                vrobot.write(str(-wmax) + ",")
                vrobot.write(str(wmax) + ";")
                sleep(0.01)
            #vrobot.write("\n")
            #vrobot.write("\n")

            start = time()

            while time() - start < tau_plat:
                #print("o")
                vrobot.write(str(-wmax+(time() - start) * epsmax) + ",")
                vrobot.write(str(wmax - (time() - start) * epsmax) + ";")
                sleep(0.01)
            vrobot.write(str(0) + ",")
            vrobot.write(str(0))

            return 0


rotation(-3.1416)
