'''
Implemente les rotations du graphisme du joueur
'''
import pygame as pg
import sys
from os import path
from settings import (
    WIDTH, HEIGHT, TITLE, FPS, TILESIZE, LIGHTGREY, BGCOLOR, 
    PLAYER_IMG, WHITE
)
from sprites import Player, Wall
from tilemap import Map, Camera

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        self.map = Map(path.join(game_folder, 'map3.txt'))
            # on remarque que le joueur a la meme taille que certains
            # emplacements et dans ce cas, il est difficile de faire 
            # coincider les deux
            
        # chargement des images
        img_folder = path.join(game_folder, 'img')
        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()

    def new(self):
        # initialise un nouveau jeu
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                    
                # le joueur est place a partir de la map
                if tile == 'P':
                    self.player = Player(self, col, row)
                    
        self.camera = Camera(self.map.width, self.map.height)
            
    def run(self):
        # boucle principale du jeu
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
            
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.draw_grid()
        # il faut ajuster la position des sprites
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            
        # part6/10: pour voir le bug, on affiche un carré représentant le joueur
        pg.draw.rect(self.screen, WHITE, self.camera.apply(self.player), 2)
        # on voit que la taille du rectangle change, nous allons changer
        # part6/18: on dessine le hit_rect
        pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)
        
        # la valeur de la "hit box"
            
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
                
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

# Creation du jeu
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
    