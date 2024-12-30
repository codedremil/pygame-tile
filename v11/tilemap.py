import pygame as pg
from settings import TILESIZE, WIDTH, HEIGHT


# on écrit notre propre fonction de détection de collision
# entre deux sprites
def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename) as f:
            for line in f:
                # ignore le '\n'
                self.data.append(line.strip())
                
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE
        
        
# classe qui simule une caméra
# Il faut calculer le décalage (offset) à partir duquel il faut dessiner la map
class Camera:
    def __init__(self, width, height):
        # taille de la camera
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        
    def apply(self, entity):
        '''entity est l'objet a deplacer'''
        return entity.rect.move(self.camera.topleft)
        
    def update(self, target):
        '''target est le sprite a suivre'''
        # correction du bug où les murs bougent
        #x = -target.rect.x + int(WIDTH / 2)
        #y = -target.rect.y + int(HEIGHT / 2)
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)
        
        # limite le scrolling
        x = min(0, x)                       # limite gauche
        x = max(-(self.width - WIDTH), x)   # limite droite
        y = min(0, y)                       # limite haute
        y = max(-(self.height - HEIGHT), y) # limite basse
        
        self.camera = pg.Rect(x, y, self.width, self.height)
        