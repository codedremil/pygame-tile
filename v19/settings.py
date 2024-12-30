import pygame as pg

vec = pg.math.Vector2   

# definitions des couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

# caractéristiques du jeu
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Démo d'un jeu basé sur des tuiles en 2D"
# changement de couleur
#BGCOLOR = DARKGREY
BGCOLOR = BROWN

TILESIZE = 32
TILESIZE = 64   # meilleure immersion
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# caractéristiques du joueur
PLAYER_SPEED = 280  # nb de pixels par seconde
PLAYER_IMG = 'manBlue_gun.png'
PLAYER_ROT_SPEED = 250
PLAYER_HIT_RECT = pg.Rect(0, 0,35, 35)  # rectangle de collision du joueur
PLAYER_HEALTH = 100

BARREL_OFFSET = vec(30, 10)  # x+30, y+10

# caractéristiques des murs
WALL_IMG = 'tileGreen_39.png'

# caractéristiques des Zombies (mobiles)
MOB_IMG = 'zombie1_hold.png'
# les Zombies auront des vitesses différentes
MOB_SPEED = 150     # moins vite que le joueur
MOB_SPEEDS = [150, 125, 100, 75]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20      # effet repulsif du mobile quand il touche le joueur
AVOID_RADIUS = 50
DETECT_RADIUS = 400

# caractéristiques du tir
BULLET_IMG = 'bullet.png'
BULLET_SPEED = 500
BULLET_LIFETIME = 1000  # en ms
BULLET_RATE = 150       # pour limiter le nb de tirs
KICKBACK = 200          # vitesse qui fait reculer le joueur quand il tire
GUN_SPREAD = 5          # ajoute une imprécision dans le tir
BULLET_DAMAGE = 10      

# Effets spéciaux
MUZZLE_FLASHES = ['whitePuff15.png', 'whitePuff16.png', 'whitePuff17.png',
                  'whitePuff18.png']
FLASH_DURATION = 40
SPLAT = 'splat green.png'   # part19/1

# valeurs des Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1

# définition des items
ITEM_IMAGES = {
    'health': 'health_pack.png',
}
HEALTH_PACK_AMOUNT = 20
BOB_RANGE = 15  # bobbing = floter/danser
BOB_SPEED = 0.4

# définitions des sons
BG_MUSIC = 'espionage.ogg'
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
                      'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav']
ZOMBIE_HIT_SOUNDS = ['splat-15.wav']
WEAPON_SOUNDS_GUN = ['sfx_weapon_singleshot2.wav']
EFFECTS_SOUNDS = {
    'level_start': 'level_start.wav',
    'health_up': 'health_pack.wav'
}
