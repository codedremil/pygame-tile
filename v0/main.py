from os import path
from sys import exit
from random import random, choice
import pygame as pg
from settings import (
    WIDTH, HEIGHT, TITLE, FPS, BGCOLOR, LIGHTGREY, TILESIZE,
    PLAYER_IMG, WALL_IMG, MOB_IMG, BULLET_IMG, PLAYER_HEALTH,
    WHITE, YELLOW, GREEN, RED, CYAN, BLACK, MOB_DAMAGE, MOB_KNOCKBACK,
    MUZZLE_FLASHES, ITEM_IMAGES, HEALTH_PACK_AMOUNT, EFFECTS_LAYER,
    BG_MUSIC, EFFECTS_SOUNDS, ZOMBIE_MOAN_SOUNDS,
    PLAYER_HIT_SOUNDS, ZOMBIE_HIT_SOUNDS, SPLAT,
    WEAPON_SOUNDS, WEAPONS,
    NIGHT_COLOR, LIGHT_MASK, LIGHT_RADIUS,
)
from sprites import Player, Wall, Mob, Obstacle, Item
from tilemap import TiledMap, Camera, collide_hit_rect

vec = pg.math.Vector2

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
        # pour améliorer le son on bufferise plus
        pg.mixer.pre_init(44100, -16, 4, 2048)        
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()
    
    def show_start_screen(self):
        pass
    
    def load_data(self):
        game_folder = path.dirname(__file__)
        self.map_folder = path.join(game_folder, 'maps')
        # self.map = TiledMap(path.join(map_folder, 'level1.tmx'))
        # self.map_img = self.map.make_map()
        # self.map_rect = self.map_img.get_rect()
        
        img_folder = path.join(game_folder, 'img')
        self.player_img = pg.image.load(
            path.join(img_folder, PLAYER_IMG)).convert_alpha()
        
        self.wall_img = pg.image.load(
            path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        
        self.mob_img = pg.image.load(
            path.join(img_folder, MOB_IMG)).convert_alpha()
        
        # il y a plusieurs formats pour la balle:
        #self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)) #.convert_apha()
        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.bullet_images['sm'] = pg.transform.scale(self.bullet_images['lg'], (10, 10))        
        
        self.splat_img = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.splat_img = pg.transform.scale(self.splat_img, (TILESIZE, TILESIZE))
        
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
            
        # chargement des sons des armes
        self.weapon_sounds = {}
        #self.weapon_sounds['gun'] = []
        #for snd in WEAPON_SOUNDS_GUN:
        #    self.weapon_sounds['gun'].append(pg.mixer.Sound(path.join(snd_folder, snd)))
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for snd in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(snd_folder, snd))
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)
                
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
            
        self.title_font = path.join(img_folder, 'ZOMBIE.TTF')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180)) # alpha channel
        
        # police zone d'affichage du nb de zombies restants
        self.hud_font = path.join(img_folder, 'Impacted2.0.ttf')
    
        # effets de lumiere
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(path.join(img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect() 
        
    
    def new(self):
        #self.all_sprites = pg.sprite.Group()
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        
        self.map = TiledMap(path.join(self.map_folder, 'level1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(
                tile_object.x + tile_object.width / 2,
                tile_object.y + tile_object.height /2)
            
            name = tile_object.name.lower()
            if name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            elif name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            elif name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                          tile_object.width, tile_object.height)
            elif tile_object.name in ITEM_IMAGES:
                Item(self, obj_center, tile_object.name)
            else:
                print(f"Objet de type inconnu: {tile_object.name}")                
        
        self.camera = Camera(self.map.width, self.map.height)
        
        # ajout d'un mode "debug" qui affichera tous les rectangles de collision
        #   on pourra vérifier les algos et que les obstacles ont bien été définis
        self.draw_debug = False
        self.effects_sounds['level_start'].play()
        self.paused = False
        self.night = False
        
    
    def run(self):
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.paused:
                self.update()
                
            self.draw()
    
    def quit(self):
        pg.quit()
        exit()
        
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
                    
                # pause on/off
                if event.key == pg.K_p:
                    self.paused = not self.paused
                    if self.paused:
                        self.start_pause_time = pg.time.get_ticks()
                    else:
                        pause_time = pg.time.get_ticks() - self.start_pause_time
                        for bullet in self.bullets:
                            bullet.spawn_time += pause_time
                            
                # nuit on/off
                if event.key == pg.K_n:
                    self.night = not self.night
            
    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)
        
        # teste la fin du jeu
        if len(self.mobs) == 0:
            self.playing = False        

        # teste si le joueur touche un Item
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                # le pack de santé ne sert que si on en a besoin !
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)  
                
            if hit.type == 'shotgun':
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.weapon = 'shotgun'

        # teste si un zombie touche le joueur
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
                
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)   # le joueur s'arrête
            if self.player.health <= 0:
                self.playing = False    # fin de jeu (TESTER: on meurt dès qu'on est touché car on est en collision trop longtemps)
                       
        if hits:
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
            self.player.hit()
            
        # teste si les zombies sont tués
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            # les zombies subissent un dommage
            # il y a plusieurs types d'armes (TESTER, puis initialiser le joueur avec le shotgun)
            # on multiplie les dommages par le nombre de bullets qui ont touché le mobile,
            # car avec le shotgun c'est possible d'être atteint par plusieurs balles
            # gere les damages du Bullet
            #hit.health -= WEAPONS[self.player.weapon]['damage'] * len(hits[hit])
            for bullet in hits[hit]:
                hit.health -= bullet.damage            
            
            hit.vel = vec(0, 0)     # et ralentit le zombie qui est touché
            
    
    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
            
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))
            
    def draw(self):
        pg.display.set_caption(f"{self.clock.get_fps():.2f}")
        #self.draw_grid()
        
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
                
            self.screen.blit(sprite.image, self.camera.apply(sprite))
          
            # affichage des hit_rect en mode debug
            # attention: les Bullets n'ont pas de hit_rect: il faut le rajouter
            if self.draw_debug:
                if hasattr(sprite, 'hit_rect'):
                    pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
                
        # affiche des hit_rect pour les murs
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)            
  
        if self.night:
            self.render_fog()
                      
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        # affiche le nb de zombies restants *
        self.draw_text(f'Zombies: {len(self.mobs)}', self.hud_font, 30, WHITE,
                       WIDTH - 10, 10, align="ne")        
        
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("En pause", self.title_font, 105, 
                           RED, WIDTH / 2, HEIGHT / 2, "center")
        
        pg.display.flip()
        

    def render_fog(self):
        # dessine le light_mask (gradient) sur l'image du brouillard
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)
                
    
    def show_go_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, 100, RED,
                       WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("Appuyez sur une touche", self.title_font, 75, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()


    def wait_for_key(self):
        pg.event.wait()     # elimine les events en cours
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()

