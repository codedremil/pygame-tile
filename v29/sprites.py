import math
from itertools import chain
import pygame as pg
import pytweening as tween
from random import uniform, choice, randint, random
from settings import (
    TILESIZE, YELLOW, GREEN, RED, BLACK,
    PLAYER_SPEED, PLAYER_ROT_SPEED, PLAYER_HIT_RECT, PLAYER_HEALTH,
    MOB_SPEED, MOB_SPEEDS, MOB_HIT_RECT, MOB_HEALTH, AVOID_RADIUS, DETECT_RADIUS,
    WEAPONS, 
    BARREL_OFFSET, DAMAGE_ALPHA, DOOR_STRENGTH,
    FLASH_DURATION,
    PLAYER_LAYER, MOB_LAYER, WALL_LAYER, BULLET_LAYER, EFFECTS_LAYER, ITEMS_LAYER,
    BOB_RANGE, BOB_SPEED
)
from tilemap import collide_hit_rect


# on simplifie en utilisant des vecteurs (calculs d'angle, ...)
vec = pg.math.Vector2


def collide_with_walls(sprite, group, dir):
    # fix bug des collisions avec les murs: comme on utilise le centre
    # du rectangle, les collisions sont détectées en divisant width et height par 2
    if dir == 'x':
        # malgré tous nos efforts ça ne marche pas car la
        # fonction de test de collisions utilise "rect" et pas "hit_rect" !
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # il faut changer le test sinon les zombies poussent le joueur dans les murs
            #if sprite.vel.x > 0:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            #if sprite.vel.x < 0:
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
            
    if dir == 'y':
        #hits = pg.sprite.spritecollide(self, self.game.walls, False)
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            #if sprite.vel.y > 0:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            #if sprite.vel.y < 0:
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y
            

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # associe le joueur et son image
        #self.image = game.player_img
        self.image = game.player_imgs['pistol'] 
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        # rectangle de collision
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        
        # il faut mémoriser l'angle de rotation
        self.rot = 0
        self.rot_speed = 0
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.weapons = ['pistol']  # armes possédées
        self.weapon = 'pistol'
        self.armour = 0   
        self.damaged = False 
        self.ammo = {self.weapon: WEAPONS[self.weapon]['ammo']} 
        self.last_hit = 0
        self.healed = False
        # augmente le spread des tirs quand le joueur bouge
        self.moving = False
        # part29
        self.target_x = None
        self.target_y = None


    # gestion des touches de déplacement
    def get_keys(self):
        # vitesse de rotation a priori
        self.rot_speed = 0
        self.vel = vec(0, 0)
            
        # part29: il faut simuler l'appui sur les touches si on dirige le joueur
        # à l'aide de la souris, en cliquant sur la map
        # d'abord, déterminer une rotation puis un déplacement
        rotate_left = rotate_right = must_move = False
        if self.target_x and self.target_y:
            target_vec = vec(self.target_x, self.target_y)
            if target_vec.distance_to(self.pos) < 5:
                self.target_x = None
                self.target_y = None
            else:
                # rotation ou déplacement ?
                dir = vec(1, 0).rotate(-self.rot)
                angle_to = dir.angle_to(target_vec - self.pos)
                #print(f"{dir=}, {target_vec=}, {angle_to=}")
                if abs(angle_to) > 3:
                    # rotation first
                    if angle_to < -180:
                        angle_to = 360 + angle_to
                    elif angle_to > 180:
                        angle_to = -(360 - angle_to)
                    if angle_to < 0:
                        rotate_left = True
                    else:
                        rotate_right = True
                else:
                    # déplacement
                    must_move = True
        
        # touches "normales" (elles peuvent annuler un déplacement à la souris)
        keys = pg.key.get_pressed()
        
        # part29: si une touche est pressée, la souris est annulée
        if any(keys):
            self.target_x = self.target_y = None
        
        # maintenant les touches RIGHT et LEFT effectuent la rotation !
        # et la touche UP avance, la touche DOWN recule moins vite !
        if keys[pg.K_LEFT] or keys[pg.K_q] or rotate_left:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d] or rotate_right:
            self.rot_speed = -PLAYER_ROT_SPEED
            
        # la vitesse s'adapte à l'arme
        if keys[pg.K_UP] or keys[pg.K_z] or must_move:
            self.vel = vec(WEAPONS[self.weapon]['player_speed'], 0).rotate(-self.rot)         
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-WEAPONS[self.weapon]['player_speed'] / 2, 0).rotate(-self.rot)
        
        if keys[pg.K_a]:
            self.lateral(90)
        if keys[pg.K_e]:
            self.lateral(-90)

        if keys[pg.K_SPACE]:
            if self.ammo[self.weapon] > 0:
                self.shoot()
            
        # touches qui permettent de choisir une arme
        if keys[pg.K_1]:
            self.weapon = 'pistol'
        if keys[pg.K_2]:
            if 'rifle' in self.weapons:
                self.weapon = 'rifle'
        if keys[pg.K_3]:
            if 'shotgun' in self.weapons:
                self.weapon = 'shotgun'
                           
            
    def lateral(self, delta):
        rot = (self.rot + delta) % 360
        vel = vec(PLAYER_SPEED // 2, 0).rotate(-rot)
        #print(f"rot={rot}, self.rot={self.rot}, vel={vel}, self.pos={self.pos}")
        self.pos += vel * self.game.dt
        
        
    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 3)    # on a besoin d'un itérateur pour next()
        
        
    def heal(self):
        self.healed = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 1)

        
    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > WEAPONS[self.weapon]['rate']:
            self.last_shot = now
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
            self.vel = vec(-WEAPONS[self.weapon]['kickback'], 0).rotate(-self.rot)
            self.ammo[self.weapon] -= 1 
                        
            for i in range(WEAPONS[self.weapon]['bullet_count']):
                # le spread augmente avec le mouvement
                spread = WEAPONS[self.weapon]['spread']
                if self.moving:
                    spread = uniform(-spread * 2, spread * 2)
                else:
                    spread = uniform(-spread, spread)
                    
                #spread = uniform(-WEAPONS[self.weapon]['spread'], WEAPONS[self.weapon]['spread'])
                # ajout du damage
                #Bullet(self.game, pos, dir.rotate(spread))
                Bullet(self.game, pos, dir.rotate(spread), WEAPONS[self.weapon]['damage'])
                snd = choice(self.game.weapon_sounds[self.weapon]) 
                # interrompre le son en cours
                if snd.get_num_channels() > 2:
                    snd.stop()
                snd.play()
            MuzzleFlash(self.game, pos) 
            
        
    # Mise à jour de la position
    def update(self):
        self.get_keys()
        
        # Check if we move (notre vecteur est de la forme vec(x, 0))
        if self.vel.x == 0:
            self.moving = False
        else:
            self.moving = True        
        
        # l'image dépend de l'arme et de l'armure
        if self.armour > 0:
            self.image = self.game.player_imgs_kevlar[self.weapon]
        else:
            self.image = self.game.player_imgs[self.weapon]
        
        self.rect = self.image.get_rect()  # ces 2 lignes ne sont pas indispensables
        self.rect.center = self.pos
        
        # ajuste l'angle de rotation: 
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        # rotation de l'image: 
        self.image = pg.transform.rotate(self.image, self.rot)
        
        # en cas de dommage on veut un effet en rouge
        if self.damaged:
            # affiche par dessus une tâche rouge avec une valeur alpha croissante
            try:
                self.image.fill((255, 0, 0, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except StopIteration:
                self.damaged = False
                
        if self.healed:
            try:
                self.image.fill((255, 255, 255, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except StopIteration:
                self.healed = False               
        
        self.pos += self.vel * self.game.dt
        
        #rotation autour du centre:
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        collide_with_walls(self, self.game.breakable_obstacles, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        collide_with_walls(self, self.game.breakable_obstacles, 'y')
        self.rect.center = self.hit_rect.center
              
        
    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH        
            

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = WALL_LAYER
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        
        
class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self._layer = WALL_LAYER 
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        
        
# Copie de la classe Obstacle        
class BreakableObstacle(pg.sprite.Sprite):
    def __init__(self, game, type, x, y):  
        self._layer = WALL_LAYER
        self.groups = game.all_sprites, game.breakable_obstacles   # groupe à part
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = type
        self.image = self.game.dest_obs_imgs[self.type].copy() # comme avec les mobiles !
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.rect.centerx = x
        self.rect.centery = y
        self.health = DOOR_STRENGTH       # pour les portes qui ont de la résistance
        self.damaged = False    # pour les effets spéciaux avec pytweening
        
        
    # effet vidéo d'un obstacle touché
    def update(self):
        if self.damaged:
            try:
                self.image.fill((250, 250, 250, next(self.damage_alpha)), 
                                special_flags=pg.BLEND_RGB_MULT)
            except StopIteration:
                self.damaged = False
                self.image = self.game.dest_obs_imgs[self.type].copy()
                
    
    def broken(self):
        if self.type in ['window_h', 'window_v']:
            rot = choice([0, 90, 180, 270])  # et ajout de la rotation ci-dessous
            self.game.map_img.blit(pg.transform.rotate(self.game.broken_window, rot), 
                        (self.rect.centerx - TILESIZE // 2, 
                         self.rect.centery - TILESIZE // 2))
            # self.game.map_img.blit(self.game.broken_window, 
            #             (self.rect.centerx - TILESIZE // 2, self.rect.centery - TILESIZE // 2))
            self.game.effects_sounds['broken_glass'].play()
            self.kill()
        elif self.type in ['door_h', 'door_v']:
            rot = choice([0, 90, 180, 270])  
            if self.health > 0:
                self.game.effects_sounds['hit_door'].play()
            else:
                # ajout de la rotation
                self.game.map_img.blit(pg.transform.rotate(self.game.broken_door, rot), 
                        (self.rect.centerx - TILESIZE // 2, 
                         self.rect.centery - TILESIZE // 2))
                self.game.effects_sounds['broken_door'].play()
                self.kill()

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 1)    
        


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y, health=MOB_HEALTH):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # on copie l'image sinon il y a un bug si on tire sur le 1er zombie
        # immobile, on affiche une barre de vie sur l'image originale, du coup
        # les autres zombies auront 2 barres de vie !
        self.image = game.mob_img.copy()
        self.my_img = game.mob_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()    
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        
        self.rect.center = self.pos
        self.health = health
        self.max_health = self.health
        
        # on veut que le zombie "pointe" vers le joueur: ajout d'une rotation
        self.rot = 0
        
        # ajout de la vitesse
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)    # quand il change de direction, il ralentit et réaccélère
        self.speed = choice(MOB_SPEEDS)
        
        # cible suivie par le zombie
        self.target = game.player
        self.damaged = False


    def update(self):
        # refactoring et prise en compte du DETECT_RADIUS
        #self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        target_dist = self.game.player.pos - self.pos
        #if target_dist.length() < DETECT_RADIUS:    # la racine carré, c'est lent !
        if target_dist.length_squared() < DETECT_RADIUS ** 2:
            # les zombies font du bruit de temps en temps
            if random() < 0.002:
                choice(self.game.zombie_moan_sounds).play()
                
            self.rot = target_dist.angle_to(vec(1, 0))
            
            self.image = pg.transform.rotate(self.my_img, self.rot)
            
            # effet vidéo quand le zombie est touché
            if self.damaged:
                try:
                    self.image.fill((0, 255, 0, next(self.damage_alpha)), special_flags=pg.BLEND_RGB_MULT)
                except StopIteration:
                    self.damaged = False            
            
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            
            # comme le Mobile n'a pas de friction, il ne s'arrête pas !
            # le vecteur est de 1 et on prend en compte les cercles d'évitement
            #self.acc = vec(MOB_SPEED, 0).rotate(-self.rot)
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()
            self.acc.scale_to_length(self.speed)
            
            self.acc += self.vel * -1 # ligne ralentir le Mobile
            self.vel += self.acc * self.game.dt
            #print(self.game.dt, self.speed, self.vel, self.acc)
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2       
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            collide_with_walls(self, self.game.breakable_obstacles, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            collide_with_walls(self, self.game.breakable_obstacles, 'y')           
            self.rect.center = self.hit_rect.center
        
        if self.health <= 0:
            # le zombie meurt avec un son aléatoire
            choice(self.game.zombie_hit_sounds).play()
            self.kill()
            # affichage de la splat image
            self.game.map_img.blit(self.game.splat, self.pos - vec(32, 32))
            
            
    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 1)
            
            
    def draw_health(self):
        if (self.health * 100 / self.max_health) > 60:
            col = GREEN
        elif (self.health * 100 / self.max_health) > 30:
            col = YELLOW
        else:
            col = RED
            
        width = int(self.rect.width * self.health / self.max_health)
        self.health_bar = pg.Rect(0, 0, width, 7)
        
        # affiche la barre différemment avec un petit cadre noir
        # if self.health < MOB_HEALTH:  # affiche que si un dommage
        #     pg.draw.rect(self.image, col, self.health_bar)
        self.health_bar.midtop = (self.rect.width / 2, 0)
        if self.health < self.max_health:
            pg.draw.rect(self.image, col, self.health_bar)
            pg.draw.rect(self.image, BLACK, self.health_bar, 2)
            
    
    # fonction d'ajustement de la direction pour éviter les autres Mobs
    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:   # on s'ignore !
                dist = self.pos - mob.pos
                # amélioration perfs
                #if 0 < dist.length() < AVOID_RADIUS:
                if 0 < dist.length_squared() < AVOID_RADIUS ** 2:
                    # le vecteur peut être nul
                    try:
                        self.acc += dist.normalize()   # calculs avec normes = 1     
                    except:
                        pass     
        
        
class Boss(Mob):
    def __init__(self, *args):
        super().__init__(health=MOB_HEALTH * 2, *args)
        self.speed *= 2
        self.image = self.game.boss_img.copy()
        self.my_img = self.game.boss_img
        
        
class Bullet(pg.sprite.Sprite):
    # les Bullets ont leur propre "damage"
    def __init__(self, game, pos, dir, damage):
        '''pos et dir sont des vecteurs'''
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # l'image dépend de l'arme
        self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]        
        
        self.rect = self.image.get_rect()
        # ajout du hit_rect pour le mode debug
        self.hit_rect = self.rect
        # copie le vecteur original
        self.pos = vec(pos)
        self.rect.center = pos
        
        # on veut que les balles (du shotgun) n'aillent pas à la même vitesse
        self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage

        
    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        
        # test de collision avec tous les sprites du mur
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        
        # il faut s'adapter au type de l'arme
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]['bullet_lifetime']:            
            self.kill()
            
        hits_d = pg.sprite.spritecollide(self, self.game.breakable_obstacles, False)
        for hit in hits_d:
            if hit.type in ['window_h', 'window_v']:
                hit.broken()
            else:
                hit.health -= WEAPONS[self.game.player.weapon]['damage']
                hit.hit()
                hit.broken()
                
            self.kill()        
            

# classe pour les effets de tir    
class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER    
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # on ajoute un peu d'aléa
        size = randint(20, 50)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()


    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()     
            
            
# classe pour les Items
class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_imgs[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.rect.center = pos
        self.pos = pos
        self.tween = tween.easeInOutSine   # choix de la fonction de tweening
        # la fonction de easing retourne une valeur entre 0 et 1
        self.step = 0
        self.dir = 1            # ou -1
        
    # animation de l'item
    # pygame n'a pas de fonction d'atténuation (easing functions)
    # (voir exemples sur le site gamemechanicexplorer.com)
    # il faut installer la librairie pytweening
    def update(self):
        # bobbing motion
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1

            