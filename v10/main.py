'''
Implemente la "vie" du joueur et des mobiles
'''
import pygame as pg
import sys
from os import path
from settings import (
    WIDTH, HEIGHT, TITLE, FPS, TILESIZE, LIGHTGREY, BGCOLOR, 
    PLAYER_IMG, WALL_IMG, MOB_IMG, BULLET_IMG, MOB_KNOCKBACK,
    BULLET_DAMAGE, MOB_DAMAGE, PLAYER_HEALTH,
    GREEN, YELLOW, RED, WHITE
)
from sprites import Player, Wall, Mob
from tilemap import Map, Camera, collide_hit_rect

vec = pg.math.Vector2

# part10/11: HUD fonctions
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
        
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)
    
        
        
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
            
        # chargement des images
        img_folder = path.join(game_folder, 'img')
        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)) #.convert_apha()

    def new(self):
        # initialise un nouveau jeu
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    Wall(self, col, row)
                    
                # le joueur est place a partir de la map
                if tile == 'P':
                    self.player = Player(self, col, row)
                    
                # ajout des Mobiles (modifier le fichier map3.txt !)
                if tile == 'M':
                    Mob(self, col, row)
                    
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
        
        # part10/8: teste si un zombie touche le joueur
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)   # le joueur s'arrête
            if self.player.health <= 0:
                self.playing = False    # fin de jeu (TESTER: on meurt dès qu'on est touché car on est en collision trop longtemps)
               
        # part10/9: quand le joueur est touché par un zombie, il recule 
        # (TESTER: c'est mieu mais le joueur est poussé dans les murs !)
        # le pb vient de la fonction collision_with_walls qui ne fait les tests que si "vel" est > 0 !
        if hits:
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
        
        # teste si les zombies sont tués
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            # part10/4: les zombies subissent un dommage
            #hit.kill()
            hit.health -= BULLET_DAMAGE
            hit.vel = vec(0, 0)     # et ralentit le zombie qui est touché
            # TESTER: puis on veut afficher une barre de "vie"

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
            
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        # plus on ajoute de sprites, plus le jeu ralentit: on
        # affiche la valeur des FPS pour surveiller les perfs 
        pg.display.set_caption(f"{self.clock.get_fps():.2f}")
        self.screen.fill(BGCOLOR)
        self.draw_grid()
        # il faut ajuster la position des sprites
        for sprite in self.all_sprites:
            # part10/6: affiche la barre de vie des mobiles (TESTER)
            # (puis on va faire pareil pour le joueur)
            if isinstance(sprite, Mob):
                sprite.draw_health()
                
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            
        # pour voir le bug, on affiche un carré représentant le joueur
        #pg.draw.rect(self.screen, WHITE, self.camera.apply(self.player), 2)
        # on voit que la taille du rectangle change, nous allons changer
        # on dessine le hit_rect
        #pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)   

        # part10/12: HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
         
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
    