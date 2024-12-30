'''
Ajout du menu pause et qq améliorations:
    en particulier on voudrait que les zombies qui meurent laissent une "trace"
'''
import pygame as pg
import sys
from os import path
from random import random, choice    # part18/14
from settings import (
    WIDTH, HEIGHT, TITLE, FPS, TILESIZE, LIGHTGREY, BGCOLOR, 
    PLAYER_IMG, WALL_IMG, MOB_IMG, BULLET_IMG, MOB_KNOCKBACK, SPLAT,
    BULLET_DAMAGE, MOB_DAMAGE, PLAYER_HEALTH,
    GREEN, YELLOW, RED, WHITE, CYAN,
    MUZZLE_FLASHES, ITEM_IMAGES, HEALTH_PACK_AMOUNT,
    EFFECTS_SOUNDS, WEAPON_SOUNDS_GUN, ZOMBIE_MOAN_SOUNDS, PLAYER_HIT_SOUNDS, 
    ZOMBIE_HIT_SOUNDS, BG_MUSIC,
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
        
        # part19/2: images des splats
        self.splat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))
        
        # chargement des effets speciaux
        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())
            
        # chargement des images des Items
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()        
            
        # chargement des sons et musiques
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
        
        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS:
            self.effects_sounds[type] = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type]))
            
        self.weapon_sounds = {}
        self.weapon_sounds['gun'] = []
        for snd in WEAPON_SOUNDS_GUN:
            self.weapon_sounds['gun'].append(pg.mixer.Sound(path.join(snd_folder, snd)))
            
        self.zombie_moan_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.2)  # réduit le volume du son des zombies
            self.zombie_moan_sounds.append(s)
            
        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))
            
        self.zombie_hit_sounds = []
        for snd in ZOMBIE_HIT_SOUNDS:
            self.zombie_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))
            
        # part19/8: chargement d'une police de caractères
        self.title_font = path.join(img_folder, 'ZOMBIE.TTF')
        
        # part19/10: chargement de l'image de dim screen
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))  # noir avec alpha channel de 180 (assez sombre)
            

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
        
        # on boucle sur les objets de la map et on crée les
        #   véritables objets en se basant sur le nom qu'on a écrit avec Tiled
        #   (attention aux majuscules et minuscules !)
        
        # on corrige un petit bug: quand l'objet est placé sur la map tuilée, 
        # il est bien centré dans la tuile mais il apparait ensuite dans le coin 
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
        #   on pourra vérifier les algos et que les obstacles ont bien été définis
        self.draw_debug = False
        self.effects_sounds['level_start'].play()
        self.paused = False     # part19/4
        
            
    def run(self):
        # boucle principale du jeu
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            # part19/6: pause (TESTER) mais il faut ajouter qqc qui montre la pause
            if not self.paused:
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
                # le pack de santé ne sert que si on en a besoin !
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)    
        
        # teste si un zombie touche le joueur
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            # part18/13
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
                
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)   # le joueur s'arrete
            if self.player.health <= 0:
                self.playing = False    # fin de jeu 
               
        # quand le joueur est touché par un zombie, il recule 
        if hits:
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
        
        # teste si les zombies sont tués
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
        
        # on affiche la map tuilée
        #self.draw_grid()
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect)) # il faut penser Ã  la camÃ©ra
            # mais la map n'est pas un sprite, il faut ajouter une fonction dans caméra
        
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
            
            
        # pour voir le bug, on affiche un carré représentant le joueur
        #pg.draw.rect(self.screen, WHITE, self.camera.apply(self.player), 2)
        # on voit que la taille du rectangle change, nous allons changer
        # on dessine le hit_rect
        #pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)   

        # HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        
        # part19/9: ajout de l'état pause (TESTER) on veut faire mieux en obscurcissant l'écran (dimming)
        if self.paused:
            # part19/11: dim screen
            #self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("En pause", self.title_font, 105, RED, WIDTH / 2, HEIGHT / 2, align="center")            
         
        pg.display.flip()
        
    # part19/7: fonction d'affichage de texte (tirée des jeux précédents)
    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)    
        

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
                    
                # part19/5: pause on/off
                if event.key == pg.K_p:
                    self.paused = not self.paused
                    

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
    