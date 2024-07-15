import pygame

from entity import Entity

from settings import *
from utils import *

class Enemy(Entity):

    def __init__(self, monster_name, pos, groups, obstacle_sprites, hit_player, death_effect):
        super().__init__(groups)

        self.sprite_type = 'enemy'
        self.obstacle_sprites = obstacle_sprites

        # Graphic setup
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]
        self.death_effect = death_effect

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

        # Player interaction
        self.can_attack = True
        self.attack_cooldown = 500
        self.attack_time = None
        self.hit_player = hit_player

        # Invincibility setup
        self.vulnerable = True
        self.hit_time = None
        self.invincibility_duration = 300

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

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0

            self.attack_time = pygame.time.get_ticks()
            self.status = 'attack'
        
        elif distance <= self.notice_radius:
            self.status = 'move'
        
        else:
            self.status = 'idle'

    def actions(self, player):
        if self.status == 'attack':
            self.hit_player(self.attack_damage, self.attack_type)
        
        elif self.status == 'move':
            self.direction = self.get_player_direction_distance(player)[0]
        
        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False

            self.frame_index = 0
        
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

        # Flicker effect on getting hit
        self.flicker()

    def cooldown(self):
        current_time = pygame.time.get_ticks()

        if not self.can_attack:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

    def take_damage(self, player, attack_type):
        if self.vulnerable:
            self.direction = self.get_player_direction_distance(player)[0]

            # if attack_type == 'weapon':
                # self.health -= player.get_full_attack_stat(attack_type)
            # else:
            print(attack_type)
            print(player.get_full_attack_stat(attack_type))
            self.health -= player.get_full_attack_stat(attack_type)

            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -self.resistance

    def check_death(self):
        if self.health <= 0:
            self.death_effect(self.rect.center, self.monster_name)
            self.kill()

    def update(self):
        self.check_death()
        self.hit_reaction()
        self.move(self.speed)
        self.animate()
        self.cooldown()

    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)
