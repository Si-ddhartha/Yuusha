import pygame

from entity import Entity

from settings import *
from utils import *

class Player(Entity):

    def __init__(self, pos, groups, obstacle_sprites, create_weapon, destroy_weapon, create_magic):
        super().__init__(groups)

        self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -25)

        # Graphics setup
        self.import_player_assets()
        self.status = 'down'

        # Movement attributes
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        # Weapon setup
        self.create_weapon = create_weapon
        self.destroy_weapon = destroy_weapon
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration = 200

        # Magic setup
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None

        # Stats
        self.stats = {
            'max_health': 100,
            'max_energy': 60,
            'attack': 6,
            'magic': 4,
            'speed': 5
        }
        self.health = self.stats['max_health']
        self.energy = self.stats['max_energy']
        self.speed = self.stats['speed']
        self.exp = 123456

        self.obstacle_sprites = obstacle_sprites
    
    def import_player_assets(self):
        player_path = '../graphics/player/'

        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
            'up_attack': [], 'down_attack': [], 'left_attack': [], 'right_attack': [],
        }

        for animation in self.animations.keys():
            full_path = player_path + animation

            self.animations[animation] = import_folder(full_path)
    
    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()  # Get keys that are pressed

            # Movement input
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            
            else:
                self.direction.y = 0       # Else the player will keep on moving
            
            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            
            else:
                self.direction.x = 0
            
            # Attack input
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_weapon()
                print('Attack')
            
            # Magic input
            if keys[pygame.K_f]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_magic(self.magic, magic_data[self.magic]['strength'] + self.stats['magic'], magic_data[self.magic]['cost'])
            
            # Switch weapon
            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()

                self.weapon_index = (self.weapon_index + 1) % len(list(weapon_data.keys()))
                self.weapon = list(weapon_data.keys())[self.weapon_index]
                print(self.weapon)

            # Switch magic
            if keys[pygame.K_e] and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()

                self.magic_index = (self.magic_index + 1) % len(list(magic_data.keys()))
                self.magic = list(magic_data.keys())[self.magic_index]
                print(self.magic)
    
    def get_status(self):
        # Check for idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status += '_idle'

        # Check for attacking status
        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0

            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle', '_attack')
                
                else:
                    self.status += '_attack'
        
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)
        
    def cooldown(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False
                self.destroy_weapon()
        
        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration:
                self.can_switch_weapon = True
        
        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration:
                self.can_switch_magic = True

    def get_full_attack_stat(self):
        return self.stats['attack'] + weapon_data[self.weapon]['damage']

    def update(self):
        self.input()
        self.move(self.speed)
        self.cooldown()
        self.get_status()
        self.animate()
