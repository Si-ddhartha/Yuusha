import pygame
from math import sin

class Entity(pygame.sprite.Sprite):

    def __init__(self, groups):
        super().__init__(groups)

        self.frame_index = 0
        self.animation_speed = 0.15
        self.direction = pygame.math.Vector2()

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')

        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        
        self.rect.center = self.hitbox.center

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # Moving right
                        self.hitbox.right = sprite.hitbox.left 
                    
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
        
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # Moving down
                        self.hitbox.bottom = sprite.hitbox.top 
                    
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom

    # Returns value of alpha when hit
    # for flicker effect
    def alpha_value(self):
        val = sin(pygame.time.get_ticks())

        if val >= 0:
            return 255
        else:
            return 0

    def flicker(self):
        if not self.vulnerable:
            alpha = self.alpha_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)
