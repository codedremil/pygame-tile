# definitions des couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# caractéristiques du jeu
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Démo d'un jeu basé sur des tuiles en 2D"
BGCOLOR = DARKGREY

TILESIZE = 32
TILESIZE = 64   # part5/2: meilleure immersion
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# caractéristiques du joueur
PLAYER_SPEED = 200  # nb de pixels par seconde
PLAYER_IMG = 'manBlue_gun.png'
