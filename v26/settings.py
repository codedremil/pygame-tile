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

# HUD settings
GUN_CIRCLE_FILL = (184, 14, 15)
GUN_CIRCLE_CENTER = (260, 40)
BG_RECT_FILL = (128, 115, 122)
KEVLAR_COLOR = (27, 99, 213)

# caractéristiques du joueur
PLAYER_SPEED = 280  # nb de pixels par seconde
PLAYER_ARMOUR = 100
PLAYER_IMG = 'manBlue_gun.png'
PLAYER_ROT_SPEED = 250
PLAYER_HIT_RECT = pg.Rect(0, 0,35, 35)  # rectangle de collision du joueur
PLAYER_HEALTH = 100

# les images du joueur dépendent de l'arme et de l'armure
PLAYER_IMGS = {
    'pistol': 'manBlue_gun.png',
    'shotgun': 'player_soff.png',
    'rifle': 'player_ak47.png'
}

PLAYER_IMGS_KEVLAR = {
    'pistol': 'player_kevlar_p2k.png',
    'shotgun': 'player_kevlar_ak47.png',
    'rifle': 'player_kevlar_soff.png'
}

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

# refactoring pour gérer plusieurs types d'armes
# caractéristiques du tir
BULLET_IMG = 'bullet.png'
 
# part26/1: ajout de ammo et max_ammo
WEAPONS = {
    'pistol': {
        'bullet_speed': 500,
        'bullet_lifetime': 1000,
        'rate': 250,
        'kickback': 200,
        'spread': 5,
        'damage': 10,
        'bullet_size': 'lg',
        'bullet_count': 1,
        'player_speed': PLAYER_SPEED,   
        'player_img': 'manBlue_gun.png',
        'ammo': 60,
        'max_ammo': 180,
    },
    'shotgun': {
        'bullet_speed': 400,
        'bullet_lifetime': 500,
        'rate': 900,
        'kickback': 300,
        'spread': 20,
        'damage': 5,
        'bullet_size': 'sm',
        'bullet_count': 12,
        'player_speed': PLAYER_SPEED // 3,    
        'player_img': 'player_shotgun.png',
        'ammo': 20,
        'max_ammo': 60,        
    },
    'rifle' : {
        'bullet_speed': 650,
        'bullet_lifetime': 1200,
        'rate': 100,
        'damage': 8,
        'kickback': 150,
        'spread': 2,
        'bullet_size': 'sm',
        'bullet_count': 1,
        'player_speed': PLAYER_SPEED - 50,
        'player_img': 'player_rifle.png',
        'ammo': 90,
        'max_ammo': 300,        
    },
}     

# Effets spéciaux
MUZZLE_FLASHES = ['whitePuff15.png', 'whitePuff16.png', 'whitePuff17.png',
                  'whitePuff18.png']
FLASH_DURATION = 40
SPLAT = 'splat green.png'
# valeurs alpha pour l'affichage des dommages subis par le joueur
DAMAGE_ALPHA = [i for i in range(0, 255, 25)]

# part23/1
NIGHT_COLOR = (20, 20, 20)
LIGHT_RADIUS = (500, 500)
LIGHT_MASK = "light_350_soft.png"

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
    'shotgun': 'obj_shotgun.png',
    'rifle': 'rifle.png',   
    'pistol': 'p2k.png',
    'kevlar': 'vest.png',
    'ammo_box': 'ammo_box.png', # part26/2
    'bullets': 'bullets.png',
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

# les sons dépendent de l'arme
#WEAPON_SOUNDS_GUN = ['sfx_weapon_singleshot2.wav']
WEAPON_SOUNDS = {
    'pistol': ['pistol.wav'],
    'shotgun': ['shotgun.wav'],
    'rifle': ['pistol.wav'], 
}

EFFECTS_SOUNDS = {
    'level_start': 'level_start.wav',
    'health_up': 'health_pack.wav',
    'gun_pickup': 'gun_pickup.wav',
}
