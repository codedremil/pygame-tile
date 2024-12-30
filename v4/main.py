'''
Implémente le scrolling map & camera
part4/1: on remplace la map par une nouvelle class Map
part4/5: on crée un map (map2.txt) plus grande que l'écran'
'''
import pygame as pg
import sys
from os import path
from settings import WIDTH, HEIGHT, TITLE, FPS, TILESIZE, LIGHTGREY, BGCOLOR
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
        # part4/3: utilise l'objet Map
        # self.map_data = []
        # with open(path.join(game_folder, 'map.txt')) as f:
        #     for line in f:
        #         self.map_data.append(line)
        # part4/6: on charge une map plus grande que l'écran (retester)
        self.map = Map(path.join(game_folder, 'map2.txt'))

    def new(self):
        # initialise un nouveau jeu
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()

        # part4/4: utilise la Map (retester)
        #for row, tiles in enumerate(self.map_data):
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                    
                # le joueur est placé à partir de la map
                if tile == 'P':
                    self.player = Player(self, col, row)
                    
        # part4/8: création de la caméra
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
        
        # part4/9
        self.camera.update(self.player)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
            
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.draw_grid()
        # part4/10: il faut ajuster la position des sprites (retester => pb)
        #self.all_sprites.draw(self.screen)
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            
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

# Création du jeu
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
    