import pygame

from settings import *
from utils import *

class Flame(pygame.sprite.Sprite):

    def __init__(self, pos, groups, sprite_type):
        super().__init__(groups)

        self.sprite_type = sprite_type

        self.frames = import_folder('../graphics/flame')
        self.frame_index = 0
        
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-10, -50)

        self.last_update = pygame.time.get_ticks()

    def animate(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_update > 100:
            self.last_update = current_time
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def update(self):
        self.animate()
