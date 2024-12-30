import pygame as pg
from settings import (
    TILESIZE, YELLOW, GREEN, PLAYER_SPEED, PLAYER_ROT_SPEED, PLAYER_HIT_RECT
)
from tilemap import collide_hit_rect


# on simplifie en utilisant des vecteurs (calculs d'angle, ...)
vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # associe le joueur et son image
        self.image = game.player_img
        self.rect = self.image.get_rect()
        # part6/12: rectangle de collision
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        
        # part6/2: il faut mémoriser l'angle de rotation
        self.rot = 0
        self.rot_speed = 0


    # gestion des touches de déplacement
    def get_keys(self):
        # part6/3: vitesse de rotation a priori
        self.rot_speed = 0
        self.vel = vec(0, 0)
            
        keys = pg.key.get_pressed()
        
        # part6/4: maintenant les touches RIGHT et LEFT effectuent la rotation !
        # et la touche UP avance, la touche DOWN recule moins vite !
        if keys[pg.K_LEFT] or keys[pg.K_q]:
            self.rot_speed = PLAYER_ROT_SPEED
            #self.vel.x = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
            #self.vel.x = PLAYER_SPEED
        if keys[pg.K_UP] or keys[pg.K_z]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
            #self.vel.y = -PLAYER_SPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
            #self.vel.y = PLAYER_SPEED
            
        # ajuste la vitesse des déplacements en diagonal (vive Pythagore !)
        if self.vel.x and self.vel.y:
            self.vel *= 0.7071  # simplification
                       
    # calcul des collisions avec les murs
    def collide_with_walls(self, dir):
        # part6/9: fix bug des collisions avec les murs: comme on utilise le centre
        # du rectangle, les collisions sont détectées en divisant width et height par 2
        # TESTER: ce n'est pas encore parfait: on a un pb quand on fait des 
        # rotations près des murs: on a l'impression de faire un saut !
        if dir == 'x':
            # part6/15: malgré tous nos efforts ça ne marche pas car la
            # fonction de test de collisions utilise "rect" et pas "hit_rect" !
            #hits = pg.sprite.spritecollide(self, self.game.walls, False)
            hits = pg.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.vel.x > 0:
                    #self.pos.x = hits[0].rect.left - self.rect.width
                    # part6/13: on remplace rect par hit_rect
                    #self.pos.x = hits[0].rect.left - self.rect.width / 2
                    self.pos.x = hits[0].rect.left - self.hit_rect.width / 2
                if self.vel.x < 0:
                    #self.pos.x = hits[0].rect.right
                    #self.pos.x = hits[0].rect.right + self.rect.width / 2
                    self.pos.x = hits[0].rect.right + self.hit_rect.width / 2
                self.vel.x = 0
                #self.rect.x = self.pos.x
                #self.rect.centerx = self.pos.x
                self.hit_rect.centerx = self.pos.x
                
        if dir == 'y':
            #hits = pg.sprite.spritecollide(self, self.game.walls, False)
            hits = pg.sprite.spritecollide(self, self.game.walls, False, collide_hit_rect)
            if hits:
                if self.vel.y > 0:
                    #self.pos.y = hits[0].rect.top - self.rect.height
                    #self.pos.y = hits[0].rect.top - self.rect.height / 2
                    self.pos.y = hits[0].rect.top - self.hit_rect.height / 2
                if self.vel.y < 0:
                    #self.pos.y = hits[0].rect.bottom
                    #self.pos.y = hits[0].rect.bottom + self.rect.height / 2
                    self.pos.y = hits[0].rect.bottom + self.hit_rect.height / 2
                self.vel.y = 0
                #self.rect.y = self.pos.y
                #self.rect.centery = self.pos.y
                self.hit_rect.centery = self.pos.y
        
    # Mise à jour de la position
    def update(self):
        self.get_keys()
        # part6/5: ajuste l'angle de rotation: TESTER et vérifier que l'image reste fixe
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        # part6/6: rotation de l'image: TESTER pb il faut tourner autour du centre du Rect !
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        self.pos += self.vel * self.game.dt
        
        # part6/7: rotation autour du centre: TESTER: quand on est au milieu du jeu
        # et qu'on effectue des rotations, les murs bougent ! En outre, les
        # collisions deviennent bizarres...
        #self.rect.x = self.pos.x
        self.rect = self.image.get_rect()
        # part6/14: là aussi rect devient hit_rect
        #self.rect.center = self.pos
        #self.rect.centerx = self.pos.x
        self.rect.center = self.pos
        self.hit_rect.centerx = self.pos.x
        self.collide_with_walls('x')
        #self.rect.y = self.pos.y
        #self.rect.centery = self.pos.y
        self.hit_rect.centery = self.pos.y
        self.collide_with_walls('y')
        # part6/15
        self.rect.center = self.hit_rect.center
            

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
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
