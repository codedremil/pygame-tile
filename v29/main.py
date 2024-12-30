'''
Gestion du joueur avec la souris
'''
import pygame as pg
import sys
from os import path
from random import random, choice    
from settings import (
    WIDTH, HEIGHT, TITLE, FPS, TILESIZE, LIGHTGREY, BGCOLOR, COOLDOWN,
    PLAYER_IMG, WALL_IMG, MOB_IMG, BULLET_IMG, MOB_KNOCKBACK, SPLAT, PLAYER_ARMOUR,
    WEAPONS, MOB_DAMAGE, PLAYER_HEALTH, PLAYER_IMGS, DEST_OBS_IMAGES,
    GREEN, YELLOW, RED, WHITE, CYAN, BLACK, KEVLAR_COLOR, PLAYER_IMGS_KEVLAR,
    MUZZLE_FLASHES, ITEM_IMAGES, HEALTH_PACK_AMOUNT, BROKEN_GLASS, BROKEN_DOOR,
    EFFECTS_SOUNDS, WEAPON_SOUNDS, ZOMBIE_MOAN_SOUNDS, PLAYER_HIT_SOUNDS, 
    ZOMBIE_HIT_SOUNDS, BG_MUSIC,
    NIGHT_COLOR, LIGHT_MASK, LIGHT_RADIUS,
    GUN_CIRCLE_CENTER, GUN_CIRCLE_FILL, BG_RECT_FILL, 
    DAY_DURATION, NIGHT_DURATION, BOSS_IMG
)
from sprites import Player, Wall, Mob, Boss, Obstacle, Item, BreakableObstacle
from tilemap import Map, TiledMap, Camera, collide_hit_rect

vec = pg.math.Vector2
  
        
class Game:
    def __init__(self):
        # pour ameliorer le son on bufferise plus
        pg.mixer.pre_init(44100, -16, 4, 2048)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.scr_width, self.scr_height = pg.display.get_surface().get_size()
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        self.map_folder = path.join(game_folder, 'maps')
              
        # chargement des images
        img_folder = path.join(game_folder, 'img')
        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.boss_img = pg.image.load(path.join(img_folder, BOSS_IMG)).convert_alpha()
        
        # charge les images du joueur en fonction de l'arme
        self.player_imgs = {}
        for item in PLAYER_IMGS:
            self.player_imgs[item] = pg.image.load(path.join(img_folder, 
                                                PLAYER_IMGS[item])).convert_alpha()

        # charges les images du joueur avec kevlar
        self.player_imgs_kevlar = {}
        for item in PLAYER_IMGS_KEVLAR:
            self.player_imgs_kevlar[item] = pg.image.load(path.join(img_folder, 
                                                PLAYER_IMGS_KEVLAR[item])).convert_alpha()
        
        # il y a plusieurs formats pour la balle:
        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.bullet_images['sm'] = pg.transform.scale(self.bullet_images['lg'], (10, 10))        
        
        self.splat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))
        self.broken_window = pg.image.load(path.join(img_folder, BROKEN_GLASS)).convert_alpha()
        self.broken_door = pg.image.load(path.join(img_folder, BROKEN_DOOR)).convert_alpha()        
        
        # chargement des effets speciaux
        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())
            
        # chargement des images des Items
        self.item_imgs = {}
        for item in ITEM_IMAGES:
            self.item_imgs[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()        

        # chargement des images des items breakable
        self.dest_obs_imgs = {}
        for dest_obs in DEST_OBS_IMAGES:
            self.dest_obs_imgs[dest_obs] = pg.image.load(path.join(img_folder, 
                                        DEST_OBS_IMAGES[dest_obs])).convert_alpha()            
        
        # chargement des sons et musiques
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
        
        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS:
            self.effects_sounds[type] = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type]))
            
        # ajuste le volume sonore des effets
        self.effects_sounds['level_start'].set_volume(0.05)
        self.effects_sounds['gun_pickup'].set_volume(0.05)
        self.effects_sounds['broken_door'].set_volume(0.1)
        self.effects_sounds['broken_glass'].set_volume(0.1)
        self.effects_sounds['hit_door'].set_volume(0.3)
        
        # chargement des sons des armes
        self.weapon_sounds = {}
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for snd in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(snd_folder, snd))
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)
            
        self.zombie_moan_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.2)  # reduit le volume du son des zombies
            self.zombie_moan_sounds.append(s)
            
        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))
            
        self.zombie_hit_sounds = []
        for snd in ZOMBIE_HIT_SOUNDS:
            self.zombie_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))
            
        # chargement d'une police de caracteres
        self.title_font = path.join(img_folder, 'ZOMBIE.TTF')
        
        # chargement de l'image de dim screen
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))  # noir avec alpha channel de 180 (assez sombre)
        
        # police zone d'affichage du nb de zombies restants
        self.hud_font = path.join(img_folder, 'Impacted2.0.ttf')  
        
        # effets de lumiere
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(path.join(img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()        
            

    def new(self):
        # initialise un nouveau jeu
        # on utilise des Sprite avec Layers
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.breakable_obstacles = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        
        self.map = TiledMap(path.join(self.map_folder, 'map1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        
        # on boucle sur les objets de la map et on cree les
        #   veritables objets en se basant sur le nom qu'on a ecrit avec Tiled
        
        # on corrige un petit bug: quand l'objet est place sur la map tuilee, 
        # il est bien centre dans la tuile mais il apparait ensuite dans le coin 
        # haut gauche de la tuile. C'est parce que object.x et object.y sont les
        # coord. du coin h-g de l'objet pas de son centre (pas pour les murs et obstacles)
        # On fait un ajustement:
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            name = tile_object.name.lower()
            if name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            elif name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            # mettre des door et window sur la map) (TESTER) (supprimer les anciens dessins !)
            elif name in ['door_h', 'door_v', 'window_h', 'window_v']:
                BreakableObstacle(self, tile_object.name.lower(), obj_center.x, obj_center.y)
            elif name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            elif name == 'boss':
                Boss(self, obj_center.x, obj_center.y)
            elif name in ITEM_IMAGES:
                Item(self, obj_center, tile_object.name)
            else:
                print(f"Objet de type inconnu: {tile_object.name}")
        
        self.camera = Camera(self.map.width, self.map.height)
        
        # ajout d'un mode "debug" qui affichera tous les rectangles de collision
        #   on pourra verifier les algos et que les obstacles ont bien ete definis
        self.draw_debug = False
        self.effects_sounds['level_start'].play()
        self.paused = False
        self.night = False
        self.night_color = 255 # WHITE
        self.day_to_night = True
        self.night_duration = 0
        self.day_duration = 0
        
            
    def run(self):
        # boucle principale du jeu
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
        sys.exit()

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
                # le pack de sante ne sert que si on en a besoin !
                hit.kill()
                self.player.heal() 
                self.effects_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
                
            # on prend l'arme si on ne l'a pas deja   
            if hit.type == 'shotgun' and 'shotgun' not in self.player.weapons:
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.weapon = 'shotgun'
                self.player.weapons.append('shotgun')
                self.player.ammo['shotgun'] = WEAPONS['shotgun']['ammo'] 
                
            if hit.type == 'rifle' and 'rifle' not in self.player.weapons:
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.weapon = 'rifle'        
                self.player.weapons.append('rifle')  
                self.player.ammo['rifle'] = WEAPONS['rifle']['ammo'] 
                
            if hit.type == 'kevlar' and self.player.armour < PLAYER_ARMOUR:
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.armour = PLAYER_ARMOUR
                
            # les bullets s'ajoutent a l'arme courante, les box a toutes les armes
            if hit.type == 'bullets':
                if self.player.ammo[self.player.weapon] < WEAPONS[self.player.weapon]['max_ammo']:
                    hit.kill()
                    self.player.ammo[self.player.weapon] += WEAPONS[self.player.weapon]['ammo'] // 2
                    if self.player.ammo[self.player.weapon] > WEAPONS[self.player.weapon]['max_ammo']:
                        self.player.ammo[self.player.weapon] = WEAPONS[self.player.weapon]['max_ammo']
                    self.effects_sounds['gun_pickup'].play()

            if hit.type == 'ammo_box':
                for weapon in self.player.weapons:
                    if self.player.ammo[weapon] < WEAPONS[weapon]['max_ammo']:
                        self.player.ammo[weapon] += WEAPONS[weapon]['ammo']
                        if self.player.ammo[weapon] > WEAPONS[weapon]['max_ammo']:
                            self.player.ammo[weapon] = WEAPONS[weapon]['max_ammo']
                        hit.kill()
                        self.effects_sounds['gun_pickup'].play()            
        
        # teste si un zombie touche le joueur
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        now = pg.time.get_ticks() 
        for hit in hits:
            # on veut un colldown car si le joueur touche trop longtemps
            # le zombie il perd trop rapidement sa vie
            if now - self.player.last_hit > COOLDOWN:
                self.player.last_hit = now
                
                # armour or health ?
                if self.player.armour > 0:
                    self.player.armour -= MOB_DAMAGE
                else:
                    self.player.health -= MOB_DAMAGE
                        
                if random() < 0.7:
                    choice(self.player_hit_sounds).play()
                    
                hit.vel = vec(0, 0)   # le joueur s'arrete
                if self.player.health <= 0:
                    self.playing = False    # fin de jeu 
               
                # en decalant ces lignes le joueur peut passer a travers
                # les zombies donc il peut s'echapper
                # quand le joueur est touche par un zombie, il recule 
                if hits:
                    self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
                    self.player.hit()
        
        # teste si les zombies sont tues
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits: # hit est un zombie (mobile)
            # les zombies subissent un dommage
            # il y a plusieurs types d'armes 
            # on multiplie les dommages par le nombre de bullets qui ont touche le mobile,
            # car avec le shotgun c'est possible d'etre atteint par plusieurs balles
            # gere les damages du Bullet
            #hit.health -= WEAPONS[self.player.weapon]['damage'] * len(hits[hit])
            for bullet in hits[hit]:
                hit.health -= bullet.damage
                
            hit.vel = vec(0, 0)     # et ralentit le zombie qui est touche
            hit.hit()
            

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
            
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

   
    def render_fog(self):
        return
        def update():
            cur = self.night_color
            if self.day_to_night:
                if self.day_duration < DAY_DURATION:
                    self.day_duration += 1
                    return cur
                
                cur -= 1
                if cur == 0:
                    self.day_to_night = False       
                    self.day_duration = 0
            else:
                if self.night_duration < NIGHT_DURATION:
                    self.night_duration += 1
                    return cur
                
                cur += 1
                if cur == 255:
                    self.day_to_night = True
                    self.night_duration = 0
                    
            return cur
            
        # dessine le light_mask (gradient) sur l'image du brouillard
        #self.fog.fill(NIGHT_COLOR)
        self.night_color = update()
        self.fog.fill((self.night_color, self.night_color, self.night_color))
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)
        

    def draw(self):
        # plus on ajoute de sprites, plus le jeu ralentit: on
        # affiche la valeur des FPS pour surveiller les perfs 
        pg.display.set_caption(f"{self.clock.get_fps():.2f}")
        
        # on affiche la map tuilee
        #self.draw_grid()
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect)) # il faut penser a la camera
            # mais la map n'est pas un sprite, il faut ajouter une fonction dans camera
        
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
            
        if True or self.night:
            self.render_fog()
            
        self.draw_hud()
        
        # ajout de l'etat pause
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))  # dimming
            self.draw_text("En pause", self.title_font, 105, RED, WIDTH / 2, HEIGHT / 2, align="center")            
         
        pg.display.flip()
        
        
    # fonction d'affichage de texte (tiree des jeux precedents)
    def draw_text(self, text, font_name, size, color, x, y, align="center"):  # (nw=>center)
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
                        self.pause_start_time = pg.time.get_ticks()
                    else:
                        pause_time = pg.time.get_ticks() - self.pause_start_time
                        for bullet in self.bullets:
                            bullet.spawn_time += pause_time
                    
                # nuit on/off
                if event.key == pg.K_n:
                    self.night = not self.night
               
            # part29/1: on ne peut pas mettre ce test dans Player.get_keys() car
            # les evenements sont principalement interceptes ici
            if event.type == pg.MOUSEWHEEL:
                print(event)  # event.y indique up (1) ou down (-1)
                
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1: # button=1=left
                    self.player.shoot()
                else: # move to target
                    #self.player.target_x = event.pos[0]
                    #self.player.target_y = event.pos[1]
                    
                    # Bug: on doit corriger par la position de la camera !
                    self.player.target_x, self.player.target_y = self.camera.shift(event.pos[0], event.pos[1])
                    

    def show_start_screen(self):
        pass


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
        

    def draw_hud(self):
        self.draw_hud_bg()
        self.draw_player_health(0, 0, self.player.health / PLAYER_HEALTH)
        self.draw_armour_health(0, 25, self.player.armour / PLAYER_ARMOUR)
        self.draw_current_gun()
        self.draw_text(f'Zombies-{len(self.mobs)}', self.hud_font, 30, BLACK, self.scr_width - 50, 50, align='ne')

    
    def draw_player_health(self, x, y, pct):
        if pct < 0:
            pct = 0
            
        BAR_LENGTH = 110
        BAR_HEIGHT = 25    
        fill = pct * BAR_LENGTH
        outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
        if pct > 0.6:
            col = GREEN
        elif pct > 0.3:
            col = YELLOW
        else:
            col = RED
            
        pg.draw.rect(self.screen, col, fill_rect)
        pg.draw.rect(self.screen, BLACK, outline_rect, 2) # WHITE => BLACK
        self.draw_text('health', self.hud_font, 20, BLACK, outline_rect.centerx, outline_rect.centery - 1)        
    
    
    def draw_current_gun(self):
        # Get the current weapon and resize it for the icon
        weapon_icon = pg.transform.scale(self.item_imgs[self.player.weapon], (48, 48))
        weapon_rect = weapon_icon.get_rect()
        weapon_rect.center = GUN_CIRCLE_CENTER
        self.draw_text(f'{self.player.weapon}', self.hud_font, 24, BLACK, 115, 1, 'nw')
        self.draw_text('ammo', self.hud_font, 20, BLACK, 115, 27, 'nw')
        self.draw_text(f'{self.player.ammo[self.player.weapon]}', self.hud_font, 20, BLACK, 180, 27, 'nw')      
        self.screen.blit(weapon_icon, weapon_rect)
        
        
    def draw_hud_bg(self):
        # Bg rect and outline
        bg_rect = pg.Rect(0, 0, 300, 80)
        bg_rect_outline = pg.Rect(0, 0, 300, 80)
        pg.draw.rect(self.screen, BG_RECT_FILL, bg_rect)
        pg.draw.rect(self.screen, BLACK, bg_rect_outline, 3)
        # Circle and outline
        pg.draw.circle(self.screen, GUN_CIRCLE_FILL, GUN_CIRCLE_CENTER, 35)
        pg.draw.circle(self.screen, BLACK, GUN_CIRCLE_CENTER, 37, 3)
        
        
    def draw_armour_health(self, x, y, pct):
        if pct < 0:
            pct = 0
        BAR_LENGTH = 110
        BAR_HEIGHT = 25
        fill = pct * BAR_LENGTH
        outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = (x, y, fill, BAR_HEIGHT)
        pg.draw.rect(self.screen, KEVLAR_COLOR, fill_rect)
        pg.draw.rect(self.screen, BLACK, outline_rect, 3)
        self.draw_text('armour', self.hud_font, 20, BLACK, outline_rect.centerx, outline_rect.centery - 1)        


# Creation du jeu
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
    
