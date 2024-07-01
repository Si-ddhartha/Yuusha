import pygame

class Tile(pygame.sprite.Sprite):

    def __init__(self, pos, groups):
        super().__init__(groups)

        self.image = pygame.image.load('../graphics/test/rock.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -10) # Shrink the rect x and y keeping the center same