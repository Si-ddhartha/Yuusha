import pygame
from random import randint

from settings import *

class MagicPlayer:

    def __init__(self, animation_player):
        self.animation_player = animation_player

    def heal(self, player, strength, cost, groups):
        if player.health != player.stats['max_health'] and player.energy >= cost:
            player.health = min(player.health + strength, player.stats['max_health'])
            player.energy -= cost

            self.animation_player.animation_particles(player.rect.center, groups, 'aura')
            self.animation_player.animation_particles(player.rect.center, groups, 'heal')

    def flame(self, player, cost, groups):
        if player.energy >= cost:
            player.energy -= cost
            player_direction = player.status.split('_')[0]

            if player_direction == 'up':
                direction = pygame.math.Vector2(0, -1)
            
            elif player_direction == 'right':
                direction = pygame.math.Vector2(1, 0)
            
            elif player_direction == 'down':
                direction = pygame.math.Vector2(0, 1)
            
            else:
                direction = pygame.math.Vector2(-1, 0)

            for i in range(1, 6):
                if direction.x:
                    offset_x = (direction.x * i) * TILESIZE
                    x = player.rect.centerx + offset_x + randint(-TILESIZE // 4, TILESIZE // 4)
                    y = player.rect.centery + randint(-TILESIZE // 4, TILESIZE // 4)

                    self.animation_player.animation_particles((x, y), groups, 'flame')
                
                else:
                    offset_y = (direction.y * i) * TILESIZE
                    x = player.rect.centerx + randint(-TILESIZE // 4, TILESIZE // 4)
                    y = player.rect.centery + offset_y + randint(-TILESIZE // 4, TILESIZE // 4)

                    self.animation_player.animation_particles((x, y), groups, 'flame')
