import pygame as pg

vec = pg.math.Vector2

WIDTH = 1024
HEIGHT = 768
TITLE = 'Mort aux zombies !'
FPS = 60

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
BGCOLOR = DARKGREY

TILESIZE = 64 #32

PLAYER_SPEED = 200
PLAYER_IMG = 'manBlue_gun.png'
PLAYER_ROT_SPEED = 250
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(30, 10)
PLAYER_HEALTH = 100

WALL_IMG = 'tileGreen_39.png'
MOB_IMG = 'zombie1_hold.png'
MOB_SPEED = 150     # moins vite que le joueur
MOB_SPEEDS = [150, 125, 100, 75]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 400

BULLET_IMG = 'bullet.png'
# BULLET_SPEED = 500
# BULLET_LIFETIME = 1000   # en ms
# BULLET_RATE = 150
# BULLET_DAMAGE = 10
# KICKBACK = 200      # force de recul lors d'un tir
# GUN_SPREAD = 5      # imprécision du tir
WEAPONS = {
    'pistol': {
        'bullet_speed': 500,
        'bullet_lifetime': 1000,
        'rate': 250,
        'kickback': 200,
        'spread': 5,
        'damage': 10,
        'bullet_size': 'lg',
        'bullet_count': 1
    },
    'shotgun': {
        'bullet_speed': 400,
        'bullet_lifetime': 500,
        'rate': 900,
        'kickback': 300,
        'spread': 20,
        'damage': 5,
        'bullet_size': 'sm',
        'bullet_count': 12
    }
}     


MUZZLE_FLASHES = ['whitePuff15.png', 'whitePuff16.png', 'whitePuff17.png',
                  'whitePuff18.png']
FLASH_DURATION = 40
SPLAT = 'splat green.png'
# valeurs alpha pour l'affichage des dommages subis par le joueur
DAMAGE_ALPHA = [i for i in range(0, 255, 25)]

NIGHT_COLOR = (20, 20, 20)
LIGHT_RADIUS = (500, 500)
LIGHT_MASK = "light_350_soft.png"

# définition des items
ITEM_IMAGES = {
    'health': 'health_pack.png',
    'shotgun': 'obj_shotgun.png',    
}
HEALTH_PACK_AMOUNT = 20 
BOB_RANGE = 15 
BOB_SPEED = 0.4

# valeurs des Layers
WALL_LAYER = 1
ITEMS_LAYER = 1
PLAYER_LAYER = 2
MOB_LAYER = 2
BULLET_LAYER = 3
EFFECTS_LAYER = 4

# définitions des sons
BG_MUSIC = 'espionage.ogg'
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
                      'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav']
ZOMBIE_HIT_SOUNDS = ['splat-15.wav']
#WEAPON_SOUNDS_GUN = ['sfx_weapon_singleshot2.wav']
WEAPON_SOUNDS = {
    'pistol': ['pistol.wav'],
    'shotgun': ['shotgun.wav']
}

EFFECTS_SOUNDS = {
    'level_start': 'level_start.wav',
    'health_up': 'health_pack.wav',
    'gun_pickup': 'gun_pickup.wav',    
}
