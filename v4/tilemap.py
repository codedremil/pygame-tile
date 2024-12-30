# part4/2: classe qui décrit la Map
import pygame as pg
from settings import TILESIZE, WIDTH, HEIGHT

class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename) as f:
            for line in f:
                # part4/12: ignore le '\n'
                #self.data.append(line)
                self.data.append(line.strip())
                
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE
        
        
# part4/7: classe qui simule une caméra
# Il faut calculer le décalage (offset) à partir duquel il faut
# dessiner la map
class Camera:
    def __init__(self, width, height):
        # taille de la caméra
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        
    def apply(self, entity):
        '''entity est l'objet Ã  déplacer'''
        return entity.rect.move(self.camera.topleft)
        
    def update(self, target):
        '''target est le sprite à suivre'''
        x = -target.rect.x + int(WIDTH / 2)
        y = -target.rect.y + int(HEIGHT / 2)
        
        # part4/11: limite le scrolling (restester => bug une colonne en trop '\n' !)
        x = min(0, x)                       # limite gauche
        x = max(-(self.width - WIDTH), x)   # limite droite
        y = min(0, y)                       # limite haute
        y = max(-(self.height - HEIGHT), y) # limite basse
        
        self.camera = pg.Rect(x, y, self.width, self.height)
        