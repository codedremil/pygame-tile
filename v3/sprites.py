'''
On veut tester les collisions des mobiles avec les murs
'''
import pygame as pg
from settings import TILESIZE, YELLOW, GREEN, PLAYER_SPEED

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        # part3/6: ajustement de la position
        # self.x = x
        # self.y = y
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.vx, self.vy = 0, 0     # part3/3

    # part3/4: gestion des touches de déplacement
    def get_keys(self):
        self.vx, self.vy = 0, 0
        # keys = pg.key.get_pressed()
        # if keys[pg.K_LEFT] or keys[pg.K_q]:
        #     self.vx = -PLAYER_SPEED
        # elif keys[pg.K_RIGHT] or keys[pg.K_d]:
        #     self.vx = PLAYER_SPEED
        # elif keys[pg.K_UP] or keys[pg.K_z]:
        #     self.vy = -PLAYER_SPEED
        # elif keys[pg.K_DOWN] or keys[pg.K_s]:
        #     self.vy = PLAYER_SPEED
            
        # part3/7: gestion des déplacements en diagonal: 
        # on remplace les elif par des if, mais les déplacements
        # en diagonal sont trop rapides
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_q]:
            self.vx = -PLAYER_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.vx = PLAYER_SPEED
        if keys[pg.K_UP] or keys[pg.K_z]:
            self.vy = -PLAYER_SPEED
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vy = PLAYER_SPEED
            
        # part3/8: ajuste la vitesse des déplacements en diagonal
        # (vive Pythagore !)
        if self.vx and self.vy:
            self.vx *= 0.7071
            self.vy *= 0.7071
            
    # part3/12: fonction devenue inutile        
    # def move(self, dx=0, dy=0):
    #     # on autorise le déplacement si pas dans le mur
    #     if not self.collide_with_walls(dx, dy):
    #         self.x += dx
    #         self.y += dy
        
    # test de collision avec les murs
    def collide_with_walls(self, dx=0, dy=0):
        for wall in self.game.walls:
            if wall.x == self.x + dx and wall.y == self.y + dy:
                return True
            
        return False

    def update(self):
        # part3/5: nouveau mode de calcul : dépend de la vitesse et du temps
        # self.rect.x = self.x * TILESIZE
        # self.rect.y = self.y * TILESIZE
        self.get_keys()
        self.x += self.vx * self.game.dt    # float (rect must be int)
        self.y += self.vy * self.game.dt
        self.rect.topleft = (self.x, self.y)
        
        # part3/9: vérifie les collisions avec les murs
        # mais cette version à un pb: parfois on ne "colle" pas au mur
        # car la distance au mur est inférieure à notre déplacement
        if pg.sprite.spritecollideany(self, self.game.walls):
            # "défait" le déplacement
            self.x -= self.vx * self.game.dt
            self.y -= self.vy * self.game.dt
            self.rect.topleft = (self.x, self.y)
            
    # part3/11: nouveau calcul des collisions
    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vx > 0:
                    self.x = hits[0].rect.left - self.rect.width
                if self.vx < 0:
                    self.x = hits[0].rect.right
                self.vx = 0
                self.rect.x = self.x
                
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vy > 0:
                    self.y = hits[0].rect.top - self.rect.height
                if self.vy < 0:
                    self.y = hits[0].rect.bottom
                self.vy = 0
                self.rect.y = self.y
        
    # part3/10: nouveau calcul des collisions
    def update(self):
        self.get_keys()
        self.x += self.vx * self.game.dt
        self.y += self.vy * self.game.dt
        self.rect.x = self.x
        self.collide_with_walls('x')
        self.rect.y = self.y
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
