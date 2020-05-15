import pygame
import numpy
import math

pygame.init()

size_x, size_y = 600, 400
scale = 50
xTopLeft, yTopLeft = (40, 40)
origine = (xTopLeft + 300, yTopLeft + 300)

espace = 50
size_x_graph,size_y_graph=400,300
origine_graph=(xTopLeft+size_x+espace,400)

xTopRight, yTopRight = (xTopLeft + size_x + size_x_graph + 2*espace, yTopLeft + size_y)
xBottomLeft, yBottomLeft = (xTopLeft, yTopLeft + size_y)
xBottomRight, yBottomRight = (xTopRight, yBottomLeft)

windowWidth, windowHeight = xTopLeft + xTopRight, yTopLeft + yBottomLeft
window = pygame.display.set_mode((windowWidth, windowHeight), pygame.SRCALPHA)
pygame.display.set_caption("Base roulante")

colors = {"black": (0, 0, 0), "blue": (0, 0, 150), "yellow": (255, 255, 0), "white": (255, 255, 255),
          "grey": (150, 150, 150), "red":(150, 0, 0)}

car_image = pygame.transform.scale(pygame.image.load("voiture.png").convert(), (32, 32))
carre_image = pygame.transform.scale(pygame.image.load("carre.png").convert(), (256, 256))

screen_rect = window.get_rect()

lines = []
lines_vitesses_gauche=[]
lines_vitesses_droite=[]
vitesses_gauche=[]
vitesses_droite=[]


class Car:
    def __init__(self, x, y, theta, image):
        self.x = x
        self.y = y
        self.image = image
        self.theta = theta
        self.original_image = car_image
        self.rect = self.image.get_rect()
        self.rect.center = (200, 200)

    def move(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta * 180 / numpy.pi -90

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_image, self.theta+90)
        x, y = self.rect.center
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.rect.center = (self.x * scale + origine[0], -self.y * scale + origine[1])  # Put the new rect's center at old center.
        # surface.blit(self.image, (self.x * 100 - 8 + size_x / 2, -self.y * 100 + 8 + size_y / 2))
        surface.blit(self.image, self.rect)


def accessible(x, y):
    return -size_x / 2 <= x <= size_x / 2 and -size_y / 2 <= y <= size_y / 2


def drawlines(surface):
    for i in range(1, size_x // scale):
        pygame.draw.line(surface, colors["grey"], (xTopLeft + i * scale, yTopLeft), (xTopLeft + i * scale, yBottomLeft))
        font = pygame.font.SysFont('Rockwell', 10)
        text = font.render("x= " + str((i - 6)), 1, colors["black"])
        surface.blit(text, (xTopLeft + i * scale - 7, yBottomLeft + 5))
    for j in range(1, size_y // scale):
        pygame.draw.line(surface, colors["grey"], (xTopLeft, yTopLeft + j * scale), (xTopLeft + size_x, yTopLeft + j * scale))
        font = pygame.font.SysFont('Rockwell', 10)
        text = font.render("y= " + str((6 - j)), 1, colors["black"])
        surface.blit(text, (10, yTopLeft + j * scale - 7))


def drawPath(surface):
    for line in lines:
        pygame.draw.line(surface, colors["black"], (origine[0] + line[0] * scale, origine[1] - line[1] * scale),
                         (origine[0] + line[2] * scale, origine[1] - line[3] * scale))


def drawGraph(surface, taille, maximum):
    nombre_sec=taille*delay+1
    nombre_rad_s=maximum
    scale_10ms= size_x_graph/nombre_sec/100 # 10 secondes réparties sur le graph
    scale_rad=size_y_graph/nombre_rad_s     # 30 rad.s-1
    for indice in range(len(lines_vitesses_gauche)):
        line=lines_vitesses_gauche[indice]
        pygame.draw.line(surface, colors["blue"], (origine_graph[0] + indice * scale_10ms, origine_graph[1] - line[0] * scale_rad),
                         (origine_graph[0] + (indice+1) * scale_10ms, origine_graph[1] - line[1] * scale_rad))
    for indice in range(len(lines_vitesses_droite)):
        line=lines_vitesses_droite[indice]
        pygame.draw.line(surface, colors["red"], (origine_graph[0] + indice * scale_10ms, origine_graph[1] - line[0] * scale_rad),
                         (origine_graph[0] + (indice+1) * scale_10ms, origine_graph[1] - line[1] * scale_rad))

    pygame.draw.line(surface, colors["black"],
                     (origine_graph[0], origine_graph[1]),
                     (origine_graph[0] + size_x_graph + 50, origine_graph[1]))
    pygame.draw.line(surface, colors["black"],
                     (origine_graph[0], origine_graph[1]),
                     (origine_graph[0], origine_graph[1] - size_y_graph - 50))

    font = pygame.font.SysFont('Rockwell', 10)

    for number in range(int(nombre_sec)+1):
        pygame.draw.line(surface, colors["black"],
                         (origine_graph[0] + number * scale_10ms * 100, origine_graph[1]- 3),
                         (origine_graph[0] + number * scale_10ms * 100, origine_graph[1] + 3))
        text = font.render(str(number), 1, colors["black"])
        surface.blit(text, (origine_graph[0] + number * scale_10ms * 100 - 2, origine_graph[1]+ 3))

    for number in range(int(nombre_rad_s)+2):
        pygame.draw.line(surface, colors["black"],
                         (origine_graph[0] -3, origine_graph[1] - number * scale_rad),
                         (origine_graph[0] +3, origine_graph[1] - number * scale_rad))
        text = font.render(str(number), 1, colors["black"])
        surface.blit(text, (origine_graph[0] - 15, origine_graph[1] - number * scale_rad))

    text = font.render("Temps (en s)", 1, colors["black"])
    surface.blit(text, (origine_graph[0] + size_x_graph + 20, origine_graph[1]+ 3))
    text = font.render("Vitesse de rotation des moteurs (en valeur absolue et en rad/s)", 1, colors["black"])
    surface.blit(text, (origine_graph[0] + 5, origine_graph[1] - size_y_graph- 60))


def ligne_theo(distance):
    tau=vmax/amax
    if distance > vmax*vmax/amax:
        plat = True
        t_plat = distance/vmax - vmax/amax
    else:
        plat = False
        tau2=numpy.sqrt(distance/amax)

    if plat:
        for nombre in range(int(tau/delay)):
            time=nombre*delay
            vitesses_droite.append(amax*time/r)
            vitesses_gauche.append(amax*time/r)
        for nombre in range(int(t_plat / delay)):
            time = nombre * delay
            vitesses_droite.append(vmax/r)
            vitesses_gauche.append(vmax/r)
        for nombre in range(int(tau/delay)):
            time = nombre * delay
            vitesses_droite.append(vmax/r-amax*time/r)
            vitesses_gauche.append(vmax/r-amax*time/r)
    else:
        for nombre in range(int(tau2/delay)):
            time = nombre * delay
            vitesses_droite.append(amax*time/r)
            vitesses_gauche.append(amax*time/r)
        for nombre in range(int(tau2 / delay)):
            time = nombre * delay
            vitesses_droite.append(amax*(tau2-time)/r)
            vitesses_gauche.append(amax*(tau2-time)/r)


def rot_theo(angle):
    tau_plat = wmax / epsmax
    tau = numpy.sqrt(L * abs(angle) / (2 * r * epsmax))
    tau2=(abs(angle) - 2*r*epsmax*tau_plat*tau_plat/L)/wmax*L/2/r
    signe=numpy.sign(angle)
    print(signe)
    if abs(angle) < 2 * r * epsmax * tau_plat * tau_plat / L:
        for nombre in range(int(tau/delay)+1):
            time = nombre * delay
            vitesses_droite.append(signe*time*epsmax)
            vitesses_gauche.append((-1)*signe*time* epsmax)
            
        for nombre in range(int(tau/delay)+1):
            time = nombre * delay
            vitesses_droite.append(signe*(tau -time)*epsmax)
            vitesses_gauche.append((-1)*signe*(tau - time)*epsmax)

    else:
        for nombre in range(int(tau_plat / delay)):
            time = nombre * delay
            vitesses_droite.append(signe * time * epsmax)
            vitesses_gauche.append((-1) * signe * time * epsmax)

        for nombre in range(int(tau2/delay)):
            time = nombre * delay
            vitesses_droite.append(signe * wmax)
            vitesses_gauche.append((-1) * signe * wmax)

        for nombre in range(int(tau_plat / delay)+1):
            time = nombre * delay
            vitesses_droite.append(signe * (tau_plat - time) * epsmax)
            vitesses_gauche.append((-1) * signe * (tau_plat - time) * epsmax)


def arc_theo(x,y,theta,xc,yc):
    dx = xc - x
    dy = yc - y

    dx_veh = -numpy.cos(theta) * dy + numpy.sin(theta) * dx
    dy_veh = numpy.sin(theta) * dy + numpy.cos(theta) * dx

    rayon = abs((dx_veh * dx_veh + dy_veh * dy_veh) / (2 * dx_veh))
    rapport = (2 * rayon - L) / (2 * rayon + L)

    if (dy_veh > 0):
        if abs(dx_veh) == rayon:
            d_ext = (rayon + L / 2) * numpy.pi / 2
        elif 0 < abs(dx_veh) < rayon:
            d_ext = (rayon + L / 2) * math.atan(dy_veh / (rayon - abs(dx_veh)))
        elif abs(dx_veh) > rayon:
            d_ext = (rayon + L / 2) * (numpy.pi + math.atan(dy_veh / (rayon - abs(dx_veh))))
        else:
            d_ext=0
    elif dy_veh<0:
        if abs(dx_veh) == rayon:
            d_ext = (rayon + L / 2) * 3 * numpy.pi / 2
        elif 0 < abs(dx_veh) < rayon:
            d_ext = (rayon + L / 2) * (2*numpy.pi+math.atan(dy_veh / (rayon - abs(dx_veh))))
        elif abs(dx_veh) > rayon:
            d_ext = (rayon + L / 2) * (numpy.pi + math.atan(dy_veh / (rayon - abs(dx_veh))))
        else:
            d_ext=0
    else:
        d_ext = (rayon + L / 2) * numpy.pi

    tau_plat = vmax / amax
    tau = numpy.sqrt(d_ext / amax)

    if d_ext >= vmax * vmax / amax:
        for nombre in range(int(tau_plat / delay)):
            time = nombre * delay
            if dx_veh < 0: #On tourne a gauche
                vitesses_droite.append((time*amax/r))
                vitesses_gauche.append(abs(rapport)*time*amax/r)
            else:
                vitesses_droite.append(abs(rapport)*time* amax/r)
                vitesses_gauche.append(time* amax/r)

        for nombre in range(int((d_ext/vmax-tau_plat) / delay)+1):
            time = nombre * delay
            if dx_veh < 0:  # On tourne a gauche
                vitesses_droite.append(vmax/r)
                vitesses_gauche.append(rapport * vmax/r)
            else:
                vitesses_droite.append(rapport * vmax/r)
                vitesses_gauche.append(vmax/r)

        for nombre in range(int(tau_plat / delay)):
            time = nombre * delay
            if dx_veh < 0:  # On tourne a gauche
                vitesses_droite.append(vmax/r - time* amax/r)
                vitesses_gauche.append(vmax*rapport/r - rapport * time * amax/r)
            else:
                vitesses_droite.append(vmax/r * rapport - rapport * time* amax/r)
                vitesses_gauche.append(vmax/r - time * amax/r)

    else:
        for nombre in range(int(tau / delay)+1):
            time = nombre * delay
            if dx_veh < 0: #On tourne a gauche
                #print("gauche")
                vitesses_droite.append(time*amax/r)
                vitesses_gauche.append(rapport*time*amax/r)
            else:
                vitesses_droite.append(rapport * time * amax/r)
                vitesses_gauche.append(time * amax/r)

        for nombre in range(int(tau_plat / delay)):
            time = nombre * delay
            if dx_veh < 0:  # On tourne a gauche
                vitesses_droite.append(amax*tau/r - time * amax/r)
                vitesses_gauche.append(rapport*(amax*tau/r - time * amax/r))
            else:
                vitesses_droite.append(rapport * (amax * tau/r - time* amax/r))
                vitesses_gauche.append(amax * tau/r - time * amax/r)
                

def start(surface, car):
    pygame.draw.rect(surface, colors["white"], (0, 0, windowWidth, windowHeight))
    drawlines(surface)
    drawPath(surface)
    car.draw(surface)
    xyFont = pygame.font.SysFont("Rockwell", 20)
    xyText = xyFont.render(("(" + str(round(car.x, 2)) + "," + str(round(car.y, 2)) + ")"), 1, colors["black"])
    surface.blit(xyText, (size_x // 2, 10))
    startFont = pygame.font.SysFont("Rockwell", 40)
    startText = startFont.render("Press SPACE to play", 1, colors["black"])
    surface.blit(startText, (700, yBottomLeft-50))
    pygame.display.update()


def updateWindow(surface, car, taille, maximum):
    pygame.draw.rect(surface, colors["white"], (0, 0, windowWidth, windowHeight))
    drawlines(surface)
    drawPath(surface)
    drawGraph(surface, taille, maximum)
    car.draw(surface)
    xyFont = pygame.font.SysFont("Rockwell", 20)
    xyText = xyFont.render(("(" + str(round(car.x,2)) + "," + str(round(car.y,2)) + ")"), 1, colors["black"])
    surface.blit(xyText, (size_x//2, 10))


def main(surface):
    #pygame.draw.rect(surface, colors["white"], (0, 0, windowWidth, windowHeight))
    running = False
    starting = True
    taille = 0
    global delay
    delay= 0.01  # 10 ms
    x, y, theta = 0, 0, numpy.pi/2
    xp, yp, vp1, vp2 = 0, 0, 0, 0
    global vmax
    vmax=1
    global amax
    amax=0.5
    global wmax
    wmax=10.5
    global epsmax
    epsmax=12.5
    global L
    L = 0.3  # ecart entre les roues
    global r
    r = 0.04  # rayon de la roue

    car = Car(0,0,theta,car_image)
    
    
    
    #ligne_theo(3)
    #rot_theo(-3*numpy.pi)
    #arc_theo(0, 0, numpy.pi/2, 3, 5)
    

    while starting:
        start(surface, car)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                starting = False
            if keys[pygame.K_SPACE]:
                starting = False
                running = True

    pygame.draw.rect(surface, colors["white"], (0, 0, windowWidth, windowHeight))
    indice = 0
    while running:
        pygame.time.delay(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # keys = pygame.key.get_pressed()
        if indice < taille:

            vit_mot1 = vitesses_droite[indice]
            vit_mot2 = vitesses_gauche[indice]

            lines_vitesses_droite.append([abs(vp1),abs(vit_mot1)])
            lines_vitesses_gauche.append([abs(vp2),abs(vit_mot2)])

            vit_rot_robot = (vit_mot1 - vit_mot2) * r / L

            # print(vit_rot_robot)
            vx = numpy.cos(theta) * (vit_mot1 + vit_mot2) * r / 2
            vy = numpy.sin(theta) * (vit_mot1 + vit_mot2) * r / 2

            x += vx * delay
            y += vy * delay
            #print("x"+str(x))
            #print(y)

            theta += vit_rot_robot * delay

            if accessible(x, y):
                car.move(x, y, theta)
                lines.append([xp, yp, x, y])
                updateWindow(surface, car, taille, maximum)
                pygame.display.update()
                xp = x
                yp = y
                vp1= vit_mot1
                vp2= vit_mot2
                indice += 1
        else:
            new_commande = False
            while not new_commande:
                commande=input("Veuillez sélectionner commande (L, R ou A) ou entrez E pour arreter la simulation: ")
                if commande == "L":
                    distance=float(input("Rentrez la longueur de la ligne: "))
                    ligne_theo(distance)
                    taille = len(vitesses_droite)
                    maximum = max(max(vitesses_droite), max(vitesses_gauche))
                    new_commande=True
                elif commande == "R":
                    angle = float(input("Rentrez la valeur de l'angle de rotation, en rad: "))
                    rot_theo(angle)
                    taille = len(vitesses_droite)
                    maximum = max(max(vitesses_droite), max(vitesses_gauche))
                    new_commande = True
                elif commande == "A":
                    xc = float(input("Rentrez la valeur de x d'arrivée souhaitée de la voiture: "))
                    yc = float(input("Rentrez la valeur de y d'arrivée souhaitée de la voiture: "))
                    arc_theo(x, y, theta, xc, yc)
                    taille = len(vitesses_droite)
                    maximum = max(max(vitesses_droite), max(vitesses_gauche))
                    new_commande= True
                elif commande == "E":
                    new_commande=True
                    running=False
                else:
                    print("Commande erronée")
            starting=True
            while starting:
                start(surface, car)
                keys = pygame.key.get_pressed()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        starting = False
                    if keys[pygame.K_SPACE]:
                        starting = False
                        running = True



    print(x)
    print(y)
    print(theta)


main(window)
