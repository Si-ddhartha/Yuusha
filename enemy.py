import pygame

from entity import Entity

from settings import *
from utils import *

class Enemy(Entity):

    def __init__(self, monster_name, pos, groups, obstacle_sprites):
        super().__init__(groups)

        self.sprite_type = 'enemy'
        self.obstacle_sprites = obstacle_sprites

        # Graphic setup
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]

        # Movement setup
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -10)

        # Stats
        self.monster_name = monster_name
        monster_info = enemy_data[monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.attack_type = monster_info['attack_type']
        self.attack_radius = monster_info['attack_radius']
        self.resistance = monster_info['resistance']
        self.notice_radius = monster_info['notice_radius']

    def import_graphics(self, name):
        base_path = f'../graphics/monsters/{name}/'

        self.animations = {'idle': [], 'move': [], 'attack': []}
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(base_path + animation)

    def get_player_direction_distance(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)

        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (direction, distance)

    def get_status(self, player):
        distance = self.get_player_direction_distance(player)[1]

        if distance <= self.attack_radius:
            self.status = 'attack'
        
        elif distance <= self.notice_radius:
            self.status = 'move'
        
        else:
            self.status = 'idle'

    def actions(self, player):
        if self.status == 'attack':
            print('enemy attacking')
        
        elif self.status == 'move':
            self.direction = self.get_player_direction_distance(player)[0]
        
        else:
            self.direction = pygame.math.Vector2()

    def update(self):
        self.move(self.speed)

    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)
