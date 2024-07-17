import pygame

from entity import Entity

from settings import *
from utils import *

class Player(Entity):

    def __init__(self, pos, groups, obstacle_sprites, create_weapon, destroy_weapon, create_magic):
        super().__init__(groups)

        self.image = pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])

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
        self.max_stats = {
            'max_health': 300,
            'max_energy': 140,
            'max_attack': 20,
            'max_magic': 10,
            'max_speed': 10
        }
        self.upgrade_cost = {
            'health': 100,
            'energy': 100,
            'attack': 100,
            'magic': 100,
            'speed': 100
        }
        self.stats = {
            'max_health': 100,
            'max_energy': 60,
            'attack': 6,
            'magic': 4,
            'speed': 5
        }
        self.health = self.stats['max_health'] * 0.1
        self.energy = self.stats['max_energy']
        # self.speed = self.stats['speed']
        self.exp = 0

        # Invincibility setup
        self.vulnerable = True
        self.hurt_time = None
        self.invincibility_duration = 500

        # Energy recovery timer
        self.energy_recovery_interval = 1500
        self.energy_recovery_timer = pygame.time.get_ticks()

        # Weapon sound
        self.weapon_attack_sound = pygame.mixer.Sound('../audio/sword.mp3')
        self.weapon_attack_sound.set_volume(0.5)

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
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            
            else:
                self.direction.y = 0       # Else the player will keep on moving
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            
            else:
                self.direction.x = 0
            
            # Attack input
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_weapon()
                self.weapon_attack_sound.play()
            
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

            # Switch magic
            if keys[pygame.K_e] and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()

                self.magic_index = (self.magic_index + 1) % len(list(magic_data.keys()))
                self.magic = list(magic_data.keys())[self.magic_index]
    
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

        # Flicker effect on getting hit
        self.flicker()
        
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

        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.vulnerable = True

    def get_full_attack_stat(self, attack_type):
        if attack_type == 'weapon':
            return self.stats['attack'] + weapon_data[self.weapon]['damage']
        
        else:
            return self.stats['magic'] + magic_data[self.magic]['strength']

    def replenish_energy(self):
        current_time = pygame.time.get_ticks()

        if self.energy < self.stats['max_energy']:
            if current_time - self.energy_recovery_timer >= self.energy_recovery_interval:
                recovery_rate = (self.energy / self.stats['max_energy']) + 0.1
                self.energy += recovery_rate
                self.energy = min(self.energy, self.stats['max_energy'])

                self.energy_recovery_timer = current_time

    def update(self):
        self.input()
        self.move(self.stats['speed'])
        self.cooldown()
        self.get_status()
        self.animate()
        self.replenish_energy()
