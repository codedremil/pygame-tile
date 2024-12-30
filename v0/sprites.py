import pygame as pg
import pytweening as tween
from itertools import chain
from random import uniform, choice, randint, random
from settings import (
    TILESIZE, YELLOW, GREEN, RED, PLAYER_SPEED, PLAYER_ROT_SPEED,
    PLAYER_HIT_RECT, MOB_SPEED, MOB_HIT_RECT, 
    BARREL_OFFSET, AVOID_RADIUS, DAMAGE_ALPHA,
    MOB_HEALTH, PLAYER_HEALTH, MOB_SPEEDS, FLASH_DURATION,
    PLAYER_LAYER, MOB_LAYER, WALL_LAYER, BULLET_LAYER, ITEMS_LAYER,
    EFFECTS_LAYER, BOB_RANGE, BOB_SPEED, DETECT_RADIUS, WEAPONS
)
from tilemap import collide_hit_rect

vec = pg.math.Vector2

def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if sprite.vel.x > 0:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if sprite.vel.x < 0:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
            
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if sprite.vel.y > 0:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if sprite.vel.y < 0:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y
            

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        #self.pos = vec(x, y) * TILESIZE
        self.pos = vec(x, y)
        self.rot = 0
        self.rot_speed = 0
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.weapon = 'pistol'
        #self.weapon = 'shotgun'
        self.damaged = False
        
        
    def get_keys(self):
        self.vel = vec(0, 0)
        self.rot_speed = 0
        
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_q]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_z]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
            
        if keys[pg.K_SPACE]:
            self.shoot()
            # now = pg.time.get_ticks()
            # if now - self.last_shot > BULLET_RATE:
            #     self.last_shot = now
            #     dir = vec(1, 0).rotate(-self.rot)
            #     pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
            #     Bullet(self.game, pos, dir)                
            #     #Bullet(self.game, self.pos, dir)
            #     self.vel = vec(-KICKBACK, 0).rotate(-self.rot)
            #     choice(self.game.weapon_sounds['gun']).play()
            #     MuzzleFlash(self.game, pos)


    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 2) 
        

    def shoot(self):
       now = pg.time.get_ticks()
       if now - self.last_shot > WEAPONS[self.weapon]['rate']:
           self.last_shot = now
           dir = vec(1, 0).rotate(-self.rot)
           pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
           self.vel = vec(-WEAPONS[self.weapon]['kickback'], 0).rotate(-self.rot)
           for i in range(WEAPONS[self.weapon]['bullet_count']):
               spread = uniform(-WEAPONS[self.weapon]['spread'], WEAPONS[self.weapon]['spread'])
               Bullet(self.game, pos, dir.rotate(spread), 
                      WEAPONS[self.weapon]['damage'])
               snd = choice(self.game.weapon_sounds[self.weapon]) 
               # interrompre le son en cours
               if snd.get_num_channels() > 2:
                   snd.stop()
               snd.play()
           MuzzleFlash(self.game, pos) 
           

    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH    

                
    def update(self):
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360        
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        
        # en cas de dommage on veut un effet en rouge
        if self.damaged:
            try:
                self.image.fill((255, 0, 0, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except StopIteration:
                self.damaged = False
                
        self.pos += self.vel * self.game.dt
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = WALL_LAYER
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        

class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._player = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img.copy()
        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        #self.pos = vec(x, y) * TILESIZE
        self.pos = vec(x, y)
        self.rect.center = self.pos
        self.rot = 0
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)    # quand il change de direction, il ralentit et réaccélère        
        self.health = MOB_HEALTH
        self.speed = choice(MOB_SPEEDS)
        self.target = game.player
        
    
    def update(self):
        target_dist = self.game.player.pos - self.pos
        if target_dist.length_squared() < DETECT_RADIUS ** 2:
            # les zombies font du bruit de temps en temps
            if random() < 0.002:
                choice(self.game.zombie_moan_sounds).play()
                
            self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
            self.image = pg.transform.rotate(self.game.mob_img, self.rot)
            self.rect = self.image.get_rect()
            self.rect.center = self.pos
            
            # comme le Mobile n'a pas de friction, il ne s'arrête pas !
            #self.acc = vec(MOB_SPEED, 0).rotate(-self.rot)
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()
            try:
                self.acc.scale_to_length(self.speed)        
            except Exception as e:
                print(e)
                print(f"{self.speed=}, {self.acc=}, {self.rot=}")
                
            self.acc += self.vel * -1 # ralentir le Mobile
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
        
        if self.health <= 0:
            choice(self.game.zombie_hit_sounds).play()
            self.kill()
            self.game.map_img.blit(self.game.splat_img, self.pos - vec(TILESIZE /2, TILESIZE / 2) )
    
    
    # fonction d'ajustement de la direction pour éviter les autres Mobs
    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:   # on s'ignore !
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                #if 0 < dist.length_squared() < AVOID_RADIUS ** 2:
                    # attention aux vecteur nuls
                    try:
                        self.acc += dist.normalize()   # calculs avec normes = 1     
                    except:
                        pass
    
    def draw_health(self):
        if (self.health * 100 / MOB_HEALTH) > 60:
            col = GREEN
        elif (self.health * 100 / MOB_HEALTH) > 30:
            col = YELLOW
        else:
            col = RED
            
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:  # affiche que si un dommage
            pg.draw.rect(self.image, col, self.health_bar) 
            
        
class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, damage):
        """pos et dir sont des vecteurs"""
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # l'image dépend de l'arme
        #self.image = game.bullet_img
        self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]        
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect   # il y aura un bug à corriger !
        self.pos = vec(pos)
        self.rect.center = pos
        #self.vel = dir.rotate(0) * BULLET_SPEED
        # ajout d'une imprécision
        #spread = uniform(-GUN_SPREAD, GUN_SPREAD)  # -5, -4, -3.., 3, 4, 5
        #self.vel = dir.rotate(spread) * BULLET_SPEED 
        self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed']
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage 
        
        
    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
            
        # il faut s'adapter au type de l'arme
        #if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]['bullet_lifetime']:            
            self.kill()
            
            
class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect   
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


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
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.rect.center = pos
        self.pos = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1
        
    def update(self):
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1
            

