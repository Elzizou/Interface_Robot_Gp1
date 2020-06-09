import pygame
import numpy
import math
from operator import add
import superpo
import basique

pygame.init()


####################################################################
### Initialisation des dimensions et des données pour la fenetre
####################################################################

tailles_lignes_x,tailles_lignes_y=10,8
size_x = 600
size_y=int(size_x*tailles_lignes_y/tailles_lignes_x)
scale = 0.5
xTopLeft, yTopLeft = (40, 60)
origine = (xTopLeft + 300, yTopLeft + 300)

espace = 50
size_x_graph,size_y_graph=400,300
origine_graph=(xTopLeft+size_x+espace,yTopLeft+400)

xTopRight, yTopRight = (xTopLeft + size_x + size_x_graph + 2*espace, yTopLeft + size_y)
xBottomLeft, yBottomLeft = (xTopLeft, yTopLeft + size_y)
xBottomRight, yBottomRight = (xTopRight, yBottomLeft)

windowWidth, windowHeight = xTopLeft + xTopRight, yTopLeft + yBottomLeft
window = pygame.display.set_mode((windowWidth, windowHeight), pygame.SRCALPHA)
pygame.display.set_caption("Base roulante")

colors = {"black": (0, 0, 0), "blue": (0, 0, 150), "yellow": (255, 255, 0), "white": (255, 255, 255),
          "grey": (150, 150, 150), "red":(150, 0, 0)}

car_image = pygame.transform.scale(pygame.image.load("voiture2.png").convert(), (32, 32))

screen_rect = window.get_rect()

lines = []
lines_vitesses_gauche = []
lines_vitesses_droite = []

####################################################################
### Classe du véhicule
####################################################################

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
        self.rect.center = (self.x *size_x/10/ scale + origine[0], -self.y/8 *size_y/ scale + origine[1])  # Put the new rect's center at old center.
        # surface.blit(self.image, (self.x * 100 - 8 + size_x / 2, -self.y * 100 + 8 + size_y / 2))
        surface.blit(self.image, self.rect)


####################################################################
### Dessin plan 2D
####################################################################

def drawlines(surface):
    for i in range(1, tailles_lignes_x):
        pygame.draw.line(surface, colors["grey"], (xTopLeft + i * size_x/tailles_lignes_x, yTopLeft),
         (xTopLeft + i * size_x/tailles_lignes_x, yBottomLeft))
        font = pygame.font.SysFont('Rockwell', 15)
        text = font.render("x= " + str(round((i - 5)*scale,1)), 1, colors["black"])
        surface.blit(text, (xTopLeft + i * size_x/tailles_lignes_x - 7, yBottomLeft + 5))
    for j in range(1, 8):
        pygame.draw.line(surface, colors["grey"], (xTopLeft, yTopLeft + j * size_y/tailles_lignes_y),
         (xTopLeft + size_x, yTopLeft + j * size_y/tailles_lignes_y))
        font = pygame.font.SysFont('Rockwell', 15)
        text = font.render("y= " + str(round((5 - j)*scale,1)), 1, colors["black"])
        surface.blit(text, (5, yTopLeft + j * size_y/tailles_lignes_y - 5))


def drawPath(surface):
    for line in lines:
        pygame.draw.line(surface, colors["black"], (origine[0] + line[0] *size_x/tailles_lignes_x/ scale, origine[1] - line[1] *size_x/tailles_lignes_x/ scale),
                         (origine[0] + line[2] *size_y/tailles_lignes_y/ scale, origine[1] - line[3] *size_y/tailles_lignes_y/ scale))


####################################################################
### Dessin graph
####################################################################

def drawGraph(surface, taille, maximum):
    nombre_sec=taille*delay+1
    nombre_rad_s=maximum
    scale_ms= size_x_graph/nombre_sec*delay
    scale_rad=size_y_graph/nombre_rad_s     # 30 rad.s-1
    for indice in range(len(lines_vitesses_gauche)):
        line=lines_vitesses_gauche[indice]
        pygame.draw.line(surface, colors["blue"], (origine_graph[0] + indice * scale_ms, origine_graph[1] - line[0] * scale_rad),
                         (origine_graph[0] + (indice+1) * scale_ms, origine_graph[1] - line[1] * scale_rad))
    for indice in range(len(lines_vitesses_droite)):
        line=lines_vitesses_droite[indice]
        pygame.draw.line(surface, colors["red"], (origine_graph[0] + indice * scale_ms, origine_graph[1] - line[0] * scale_rad),
                         (origine_graph[0] + (indice+1) * scale_ms, origine_graph[1] - line[1] * scale_rad))

    pygame.draw.line(surface, colors["black"],
                     (origine_graph[0], origine_graph[1]),
                     (origine_graph[0] + size_x_graph + 50, origine_graph[1]))
    pygame.draw.line(surface, colors["black"],
                     (origine_graph[0], origine_graph[1]),
                     (origine_graph[0], origine_graph[1] - size_y_graph - 50))

    font = pygame.font.SysFont('Rockwell', 10)

    for number in range(int(nombre_sec)+1):
        pygame.draw.line(surface, colors["black"],
                         (origine_graph[0] + number * scale_ms * 100, origine_graph[1]- 3),
                         (origine_graph[0] + number * scale_ms * 100, origine_graph[1] + 3))
        text = font.render(str(number), 1, colors["black"])
        surface.blit(text, (origine_graph[0] + number * scale_ms * 100 - 2, origine_graph[1]+ 3))

    for number in range(int(nombre_rad_s)+2):
        pygame.draw.line(surface, colors["black"],
                         (origine_graph[0] -3, origine_graph[1] - number * scale_rad),
                         (origine_graph[0] +3, origine_graph[1] - number * scale_rad))
        text = font.render(str(number), 1, colors["black"])
        surface.blit(text, (origine_graph[0] - 15, origine_graph[1] - number * scale_rad-5))

    text = font.render("Temps (en s)", 1, colors["black"])
    surface.blit(text, (origine_graph[0] + size_x_graph-20, origine_graph[1]+ 20))
    text = font.render("Vitesse de rotation des moteurs (en rad/s)", 1, colors["black"])
    surface.blit(text, (origine_graph[0] + 5, origine_graph[1] - size_y_graph- 60))


####################################################################
### Fonctions update
####################################################################


def start(surface, car):
    pygame.draw.rect(surface, colors["white"], (0, 0, windowWidth, windowHeight))
    drawlines(surface)
    drawPath(surface)
    car.draw(surface)
    xyFont = pygame.font.SysFont("Rockwell", 20)
    xyText = xyFont.render(("(" + str(round(car.x, 2)) + "," + str(round(car.y, 2)) + "," + str(round(car.theta*180/numpy.pi,2))+"°)"), 1, colors["black"])
    surface.blit(xyText, (size_x // 2, yTopLeft-30))
    startFont = pygame.font.SysFont("Rockwell", 40)
    startText = startFont.render("Press SPACE to play", 1, colors["black"])
    surface.blit(startText, (700, yBottomLeft-50))
    titleFont = pygame.font.SysFont("Calibri", 30, True)
    titleText = titleFont.render("Simulation du robot", 1, colors["black"])
    surface.blit(titleText, (size_x //4*3, 0))
    pygame.display.update()


def updateWindow(surface, car, taille, maximum):
    pygame.draw.rect(surface, colors["white"], (0, 0, windowWidth, windowHeight))
    drawlines(surface)
    drawPath(surface)
    drawGraph(surface, taille, maximum)
    car.draw(surface)
    xyFont = pygame.font.SysFont("Rockwell", 20)
    xyText = xyFont.render(("(" + str(round(car.x,2)) + "," + str(round(car.y,2)) + "," + str(round(90+car.theta,1))+"°)"), 1, colors["black"])
    surface.blit(xyText, (size_x//2, yTopLeft-30))
    titleFont = pygame.font.SysFont("Calibri", 30,True)
    titleText = titleFont.render("Simulation du robot", 1, colors["black"])
    surface.blit(titleText, (size_x//4*3, 0))


####################################################################
### Main
####################################################################


def main(surface,type):
    ####################################################################
    ### Initialisation des données
    ####################################################################
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

    ####################################################################
    ### Récupération des vitesses
    ####################################################################

    if type=="superpo":
        vitesses_droit, vitesses_gauche = superpo.main()
    elif type=="joystick":
        delay=0.1
        vitesses_file=open("vitesse.txt","r")
        vitesses=vitesses_file.readlines()
        vitesses_droit, vitesses_gauche = [],[]
        for i in range(0,len(vitesses)-1,2):
            vitesses_droit.append(float(vitesses[i]))
            vitesses_gauche.append(float(vitesses[i+1]))
    elif type=="basique":
        vitesses_droit, vitesses_gauche = basique.main()


    taille=len(vitesses_gauche)
    maximum = max(max(vitesses_droit), max(vitesses_gauche))

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

        ####################################################################
        ### Calculs et mise à jour sur les graphiques
        ####################################################################

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # keys = pygame.key.get_pressed()
        if indice < taille:


            vit_mot1 = vitesses_droit[indice]
            vit_mot2 = vitesses_gauche[indice]

            lines_vitesses_droite.append([vp1,vit_mot1])
            lines_vitesses_gauche.append([vp2,vit_mot2])

            vit_rot_robot = (vit_mot1 - vit_mot2) * r / L

            vx = numpy.cos(theta) * (vit_mot1 + vit_mot2) * r / 2
            vy = numpy.sin(theta) * (vit_mot1 + vit_mot2) * r / 2

            x += vx * delay
            y += vy * delay

            theta += vit_rot_robot * delay


            car.move(x, y, theta)
            lines.append([xp, yp, x, y])
            updateWindow(surface, car, taille, maximum)
            pygame.display.update()
            xp = x
            yp = y
            vp1= vit_mot1
            vp2= vit_mot2
            indice += 1

    print(x)
    print(y)
    print(theta)


main(window,"superpo")
