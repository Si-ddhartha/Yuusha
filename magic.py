import pygame

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

    def flame(self):
        pass
