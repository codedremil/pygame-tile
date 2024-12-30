import pygame as pg
from random import uniform
from settings import (
    TILESIZE, YELLOW, GREEN, RED,
    PLAYER_SPEED, PLAYER_ROT_SPEED, PLAYER_HIT_RECT, PLAYER_HEALTH,
    MOB_SPEED, MOB_HIT_RECT, MOB_HEALTH,
    BULLET_SPEED, BULLET_LIFETIME, BULLET_RATE, 
    BARREL_OFFSET, KICKBACK, GUN_SPREAD
)
from tilemap import collide_hit_rect


# on simplifie en utilisant des vecteurs (calculs d'angle, ...)
vec = pg.math.Vector2


def collide_with_walls(sprite, group, dir):
    # fix bug des collisions avec les murs: comme on utilise le centre
    # du rectangle, les collisions sont détectées en divisant width et height par 2
    # TESTER: ce n'est pas encore parfait: on a un pb quand on fait des 
    # rotations près des murs: on a l'impression de faire un saut !
    if dir == 'x':
        # malgré tous nos efforts ça ne marche pas car la
        # fonction de test de collisions utilise "rect" et pas "hit_rect" !
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            # il faut changer le test sinon les zombies possuent le joueur dans les murs
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
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # associe le joueur et son image
        self.image = game.player_img
        self.rect = self.image.get_rect()
        # rectangle de collision
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        #part13/5: attention !
        #self.pos = vec(x, y) * TILESIZE
        self.pos = vec(x, y)
        
        # il faut mémoriser l'angle de rotation
        self.rot = 0
        self.rot_speed = 0
        
        self.last_shot = 0
        self.health = PLAYER_HEALTH   # part10/7


    # gestion des touches de déplacement
    def get_keys(self):
        # vitesse de rotation a priori
        self.rot_speed = 0
        self.vel = vec(0, 0)
            
        keys = pg.key.get_pressed()
        
        # maintenant les touches RIGHT et LEFT effectuent la rotation !
        # et la touche UP avance, la touche DOWN recule moins vite !
        if keys[pg.K_LEFT] or keys[pg.K_q]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_z]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)

        # lancement d'un tir
        if keys[pg.K_SPACE]:
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1, 0).rotate(-self.rot)

                # ajustement du départ de la balle
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                Bullet(self.game, pos, dir)
                self.vel = vec(-KICKBACK, 0).rotate(-self.rot)
            
        # ajuste la vitesse des déplacements en diagonal (vive Pythagore !)
        if self.vel.x and self.vel.y:
            self.vel *= 0.7071  # simplification
        
        
    # Mise à jour de la position
    def update(self):
        self.get_keys()
        # ajuste l'angle de rotation: 
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        # rotation de l'image: 
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        self.pos += self.vel * self.game.dt
        
        #rotation autour du centre:
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
            

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
        
        
# part13/4: création des objets Obstacle (TESTER)
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


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        # image du mur: TESTER, mais on voit que parfois le
        # Sprite du joueur est "sous" les murs: il faut implémenter les Layers
        self.game = game
        self.image = game.mob_img
        self.rect = self.image.get_rect()
        self.hit_rect = MOB_HIT_RECT.copy()    
        self.hit_rect.center = self.rect.center
        # part13/9: attention !
        #self.pos = vec(x, y) * TILESIZE
        self.pos = vec(x, y)
        
        self.rect.center = self.pos
        self.health = MOB_HEALTH    
        
        # on veut que le zombie "pointe" vers le joueur: ajout d'une rotation
        self.rot = 0
        
        # ajout de la vitesse
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)    # quand il change de direction, il ralentit et réaccélère


    def update(self):
        # montrer les figures pour comprendre le calcul
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        
        # comme le Mobile n'a pas de friction, il ne s'arrête pas !
        self.acc = vec(MOB_SPEED, 0).rotate(-self.rot)
        self.acc += self.vel * -1 # ligne ralentir le Mobile
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2       
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        
        if self.health <= 0:
            self.kill()
            
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
    def __init__(self, game, pos, dir):
        '''pos et dir sont des vecteurs'''
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_img
        self.rect = self.image.get_rect()
        # part13/13: ajout du hit_rect pour le mode debug
        self.hit_rect = self.rect
        # copie le vecteur original
        self.pos = vec(pos)
        self.rect.center = pos
        
        # ajout de l'imprécision dans le tir
        spread = uniform(-GUN_SPREAD, GUN_SPREAD)  # -5, -4, -3.., 3, 4, 5
        self.vel = dir.rotate(spread) * BULLET_SPEED        
        self.spawn_time = pg.time.get_ticks()
        
    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        
        # test de collision avec tous les sprites du mur
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        
        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()
            
     