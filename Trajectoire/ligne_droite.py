from time import *
from math import *

### Code de la route ###
vmax = 1 #en m/s (en vrai je crois que c'est 0.42, a verifier)
amax = 0.5 #en m/s^2 (la ca correspond a la valeur de r et epsmax

### Contraintes techniques ###
wmax = 10.5   #en rad s-1
epsmax = 12.5 #en rad.s-2
r = 0.04      #4cm
L = 0.3       #30cm


### Variables utiles au prgm ###
plat = 2
start = 0

### Valeurs caracteristiques
tau = vmax/amax


def ligne_droite (distance):

    global t_plat
    fichier = open("vrobot_ligne", "w")

    if distance > vmax*vmax/amax:
        plat = 1
        t_plat = distance/vmax - vmax/amax
    else:
        plat = 0

    start = time()

    if plat == 1:
        while time()-start < tau:
            fichier.write(str((time()-start) * amax/r) + ",")
            fichier.write(str((time()-start) * amax/r) + ";")
            sleep(0.01)
        #fichier.write("\n")
        start = time()
        while time()-start < t_plat:
            fichier.write(str(vmax/r) + ",")
            fichier.write(str(vmax/r) + ";")
            sleep(0.01)
        #fichier.write("\n")
        start = time()
        while vmax > (time()-start)*amax:
            fichier.write(str((vmax-(time()-start)*amax)/r) + ",")
            fichier.write(str((vmax-(time()-start)*amax)/r) + ";")
            sleep(0.01)
        fichier.write(str(0) + ",")
        fichier.write(str(0))
        return 0

    elif plat == 0:
        while time()-start < sqrt(distance/amax):
            fichier.write(str((time() - start) * amax/r) + ",")
            fichier.write(str((time() - start) * amax/r) + ";")
            #fichier.write(" ; ")
            sleep(0.01)
        #fichier.write("\n")
        start = time()
        while sqrt(distance*amax) > (time()-start)*amax:
            fichier.write(str((sqrt(amax*distance)-(time()-start)*amax)/r) + ",")
            fichier.write(str((sqrt(amax*distance)-(time()-start)*amax)/r) + ";")
            #fichier.write(" ; ")
            sleep(0.01)
        fichier.write(str(0) + ",")
        fichier.write(str(0))
        return 0

    else:
        return 1

ligne_droite(3)
