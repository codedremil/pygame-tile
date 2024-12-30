import pygame as pg

vec = pg.math.Vector2   # part9/8

# definitions des couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)

# caractéristiques du jeu
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Démo d'un jeu basé sur des tuiles en 2D"
# changement de couleur
#BGCOLOR = DARKGREY
BGCOLOR = BROWN

TILESIZE = 32
TILESIZE = 64   # part5/2: meilleure immersion
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# caractéristiques du joueur
PLAYER_SPEED = 200  # nb de pixels par seconde
PLAYER_IMG = 'manBlue_gun.png'
PLAYER_ROT_SPEED = 250
PLAYER_HIT_RECT = pg.Rect(0, 0,35, 35)  # rectangle de collision du joueur

# part9/8
BARREL_OFFSET = vec(30, 10)  # x+30, y+10

# caractéristiques des murs
WALL_IMG = 'tileGreen_39.png'

# caractéristiques des Zombies (mobiles)
MOB_IMG = 'zombie1_hold.png'
MOB_SPEED = 150     # moins vite que le joueur
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)    

# part9/1: caractéristiques du tir
BULLET_IMG = 'bullet.png'
BULLET_SPEED = 500
BULLET_LIFETIME = 1000  # en ms
BULLET_RATE = 150       # pour limiter le nb de tirs
KICKBACK = 200          # part9/10: vitesse qui fait reculer le joueur quand il tire
GUN_SPREAD = 5          # part9/11: ajoute une imprécision dans le tir
