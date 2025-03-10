import pygame
from settings import *

class Tile(pygame.sprite.Sprite):

    def __init__(self, pos, groups, sprite_type, surface = pygame.Surface((TILESIZE, TILESIZE))):
        super().__init__(groups)

        self.sprite_type = sprite_type
        self.image = surface

        if self.sprite_type == 'object':
            self.rect = self.image.get_rect(topleft = (pos[0], pos[1] - TILESIZE))
        
        else:
            self.rect = self.image.get_rect(topleft = pos)
        
        self.hitbox = self.rect.inflate(0, HITBOX_OFFSET[self.sprite_type]) # Shrink the rect x and y keeping the center same