import pygame as pg
from settings import TILESIZE, YELLOW, GREEN, PLAYER_SPEED

# part5/3: on simplifie en utilisant des veteurs (calculs d'angle, ...)
vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        
        # part5/14: associe le joueur et son image
        #self.image = pg.Surface((TILESIZE, TILESIZE))
        #self.image.fill(YELLOW)
        self.image = game.player_img
        
        self.rect = self.image.get_rect()
        # part5/4
        self.vel = vec(0, 0)
        self.pos = vec(x, y) * TILESIZE
        # self.x = x * TILESIZE
        # self.y = y * TILESIZE
        # self.vx, self.vy = 0, 0

    # gestion des touches de déplacement
    def get_keys(self):
        # part5/5
        self.vel = vec(0, 0)
        #self.vx, self.vy = 0, 0
            
        # gestion des déplacements en diagonal: 
        # on remplace les elif par des if, mais les déplacements
        # en diagonal sont trop rapides
        keys = pg.key.get_pressed()
        
        # part5/6: utilisation du vecteur
        if keys[pg.K_LEFT] or keys[pg.K_q]:
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vel.x = PLAYER_SPEED
        if keys[pg.K_UP] or keys[pg.K_z]:
            self.vel.y = -PLAYER_SPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel.y = PLAYER_SPEED
            
        # ajuste la vitesse des déplacements en diagonal
        # (vive Pythagore !)
        if self.vel.x and self.vel.y:
            self.vel *= 0.7071  # part5/7: simplification
                       
    # calcul des collisions avec les murs
    # part5/11: remplace vx par vel.x, vy par vel.y, x par pos.x et y par pos.y
    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x
                
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y
        
    # Mise à jour de la position
    def update(self):
        self.get_keys()
        # part5/9: simplification
        self.pos += self.vel * self.game.dt
        # self.x += self.vx * self.game.dt
        # self.y += self.vy * self.game.dt
        
        # part5/10: maj x => pos.x
        #self.rect.x = self.x
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        #self.rect.y = self.y
        self.rect.y = self.pos.y
        self.collide_with_walls('y')
            

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
