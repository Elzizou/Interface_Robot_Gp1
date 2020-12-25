import numpy as np
import matplotlib.pyplot as plt

Kp,Ki,Kd=0.05,50,0
wmax=100*2*np.pi/60
r=0.04
amax=0.5
n=250
deltat=0.010

temps_avant_plateau=40 #0.4 s = temps entre le début de la décéleration et le deuxieme plateau
temps_plateau=50       #0.5 s = temps du deuxieme plateau

Wd=[wmax for k in range(n)]

def new_Wd(n): #On prend un temps assez long pour qu'il y ait un plateau
    Wd=[]
    m=int(wmax/amax*r/deltat)
    indices=[m,n-m-temps_plateau, n-m-temps_plateau+temps_avant_plateau,n-m+temps_avant_plateau]
    for k in range(indices[0]):
        Wd.append(wmax*k/m)
    for k in range(indices[0], indices[1]):
        Wd.append(wmax)
    for k in range(indices[1],indices[2]):
        Wd.append(wmax-wmax*(k-indices[1])/m)
    for k in range (indices[2],indices[3]):
        Wd.append(Wd[indices[2]-1])
    for k in range(indices[3],n):
        Wd.append(wmax-wmax*(k-indices[3]+(indices[2]-indices[1]))/m)
    return Wd


def main(vit_rot_mot_d,deltat):
    epsilon_prev=0
    i_epsilon=0
    W=[0]
    for k in range (n-1):
        epsilon = vit_rot_mot_d[k]-  W[k];
        d_epsilon=(epsilon-epsilon_prev)/deltat;
        i_epsilon+=epsilon_prev*deltat;
        u=Kp*epsilon+Ki*i_epsilon+Kd*d_epsilon;
        W.append(u*wmax/12)
        epsilon_prev=epsilon
    
    plt.figure("PID")
    t=np.linspace(deltat,n*deltat,n)
    plt.plot(t,W,"red")
    plt.plot(t,vit_rot_mot_d,"blue")
    plt.grid()
    plt.show()
    print(i_epsilon)

main(new_Wd(n),deltat)