'''
Ajout des animations des objets
'''
import pygame as pg
import sys
from os import path
from settings import (
    WIDTH, HEIGHT, TITLE, FPS, TILESIZE, LIGHTGREY, BGCOLOR, 
    PLAYER_IMG, WALL_IMG, MOB_IMG, BULLET_IMG, MOB_KNOCKBACK,
    BULLET_DAMAGE, MOB_DAMAGE, PLAYER_HEALTH,
    GREEN, YELLOW, RED, WHITE, CYAN,
    MUZZLE_FLASHES, ITEM_IMAGES, HEALTH_PACK_AMOUNT
)
from sprites import Player, Wall, Mob, Obstacle, Item
from tilemap import Map, TiledMap, Camera, collide_hit_rect

vec = pg.math.Vector2

# HUD fonctions
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
        map_folder = path.join(game_folder, 'maps')
       
        # chargement de la nouvelle map
        #self.map = Map(path.join(game_folder, 'map3.txt'))
        self.map = TiledMap(path.join(map_folder, 'level1.tmx'))  
        
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
            
        # chargement des images
        img_folder = path.join(game_folder, 'img')
        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)) #.convert_apha()
        
        # chargement des effets speciaux
        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())
            
        # chargement des images des Items
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()        

    def new(self):
        # initialise un nouveau jeu
        # on utilise des Sprite avec Layers
        #self.all_sprites = pg.sprite.Group()
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()      # part16/4

        # code inutile maintenant !
        # for row, tiles in enumerate(self.map.data):
        #     for col, tile in enumerate(tiles):
        #         if tile == '1':
        #             Wall(self, col, row)
                    
        #         # le joueur est place a partir de la map
        #         if tile == 'P':
        #             self.player = Player(self, col, row)
                    
        #         # ajout des Mobiles (modifier le fichier map3.txt !)
        #         if tile == 'M':
        #             Mob(self, col, row)
        
        # on boucle sur les objets de la map et on cr�e les
        #   v�ritables objets en se basant sur le nom qu'on a �crit avec Tiled
        #   (attention aux majuscules et minuscules !)
        
        # on corrige un petit bug: quand l'objet est plac� sur la map tuil�e, 
        # il est bien centr� dans la tuile mais il apparait ensuite dans le coin 
        # haut gauche de la tuile. C'est parce que object.x et object.y sont les
        # coord. du coin h-g de l'objet pas de son centre (pas pour les murs et obstacles)
        # On fait un ajustement:
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            
            if tile_object.name.lower() == 'player':
                #self.player = Player(self, tile_object.x, tile_object.y)
                self.player = Player(self, obj_center.x, obj_center.y)
            elif tile_object.name.lower() == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            elif tile_object.name.lower() == 'zombie':
                #Mob(self, tile_object.x, tile_object.y)
                Mob(self, obj_center.x, obj_center.y)
            elif tile_object.name in ITEM_IMAGES:
                Item(self, obj_center, tile_object.name)
            else:
                print(f"Objet de type inconnu: {tile_object.name}")
        
        
        self.camera = Camera(self.map.width, self.map.height)
        
        # ajout d'un mode "debug" qui affichera tous les rectangles de collision
        #   on pourra v�rifier les algos et que les obstacles ont bien �t� d�finis
        self.draw_debug = False
        
            
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
        
        # teste si le joueur touche un Item
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                # le pack de sant� ne sert que si on en a besoin !
                hit.kill()
                self.player.add_health(HEALTH_PACK_AMOUNT)    # part16/9: � ajouter    
        
        # teste si un zombie touche le joueur
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)   # le joueur s'arrête
            if self.player.health <= 0:
                self.playing = False    # fin de jeu 
               
        # quand le joueur est touch� par un zombie, il recule 
        if hits:
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
        
        # teste si les zombies sont tu�s
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            # les zombies subissent un dommage
            hit.health -= BULLET_DAMAGE
            hit.vel = vec(0, 0)     # et ralentit le zombie qui est touché

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
            
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        # plus on ajoute de sprites, plus le jeu ralentit: on
        # affiche la valeur des FPS pour surveiller les perfs 
        pg.display.set_caption(f"{self.clock.get_fps():.2f}")
        
        # on affiche la map tuil�e
        #self.draw_grid()
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect)) # il faut penser à la caméra
            # mais la map n'est pas un sprite, il faut ajouter une fonction dans cam�ra
        
        # il faut ajuster la position des sprites
        for sprite in self.all_sprites:
            # affiche la barre de vie des mobiles
            if isinstance(sprite, Mob):
                sprite.draw_health()
                
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            
            # affichage des hit_rect en mode debug
            # attention: les Bullets n'ont pas de hit_rect: il faut le rajouter
            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
                
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)            
            
            
        # pour voir le bug, on affiche un carr� repr�sentant le joueur
        #pg.draw.rect(self.screen, WHITE, self.camera.apply(self.player), 2)
        # on voit que la taille du rectangle change, nous allons changer
        # on dessine le hit_rect
        #pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)   

        # HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
         
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
                
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                    
                # mode debug on/off
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                    

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
    