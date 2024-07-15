import pygame
from random import choice, randint

from settings import *
from utils import *
from debug import *

from ui import UI
from tile import Tile
from player import Player
from weapon import Weapon
from magic import MagicPlayer
from enemy import Enemy
from particles import AnimationPlayer

class Level:

    def __init__(self):
        # Get the display surface
        self.display_surface = pygame.display.get_surface()

        # UI setup
        self.ui = UI()

        # Sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # Attack sprites
        self.current_attack = None

        # Particles
        self.animation_player = AnimationPlayer()

        # Magic
        self.magic_player = MagicPlayer(self.animation_player)

        self.create_map()
    
    def create_map(self):
        layouts = {
            'boundary': import_csv_layout('../map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('../map/map_Grass.csv'),
            'objects': import_csv_layout('../map/map_Objects.csv'),
            'entities': import_csv_layout('../map/map_Entities.csv')
        }

        graphics = {
            'grass': import_folder('../graphics/Grass'),
            'objects': import_folder('../graphics/objects')
        }

        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in  enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE

                        if style == 'boundary':
                            Tile((x, y), [self.obstacle_sprites], 'invisible')
                        
                        if style == 'grass':
                            random_grass_img = choice(graphics['grass'])
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], 'grass', random_grass_img)
                        
                        if style == 'objects':
                            object_img = graphics['objects'][int(col)]

                            if col == '23': # Snow grass
                                Tile((x, y), [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites], 'grass', object_img)
                            else:
                                Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object', object_img)

                        if style == 'entities':
                            if col == '394':
                                self.player = Player((x + 20, y + 7), [self.visible_sprites], self.obstacle_sprites, self.create_weapon, self.destroy_weapon, self.create_magic)
                            
                            else:
                                if col == '390':
                                    monster_name = 'bamboo'
                                elif col == '391':
                                    monster_name = 'spirit'
                                elif col == '392':
                                    monster_name = 'raccoon'
                                else:
                                    monster_name = 'squid'

                                Enemy(monster_name, 
                                        (x, y), 
                                        [self.visible_sprites, self.attackable_sprites], 
                                        self.obstacle_sprites, 
                                        self.player_hit, 
                                        self.enemy_death_effect)

    def create_weapon(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])

        elif style == 'flame':
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])

    def destroy_weapon(self):
        if self.current_attack:
            self.current_attack.kill()
        
        self.current_attack = None

    def player_attack(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                attacked_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)

                if attacked_sprites:
                    for target_sprite in attacked_sprites:
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 75)

                            for leaf in range(randint(3, 6)):
                                self.animation_player.grass_particles(pos - offset, [self.visible_sprites])

                            target_sprite.kill()

                        else:
                            target_sprite.take_damage(self.player, attack_sprite.sprite_type)

    def player_hit(self, damage_amount, attack_type):
        if self.player.vulnerable:
            self.player.health -= damage_amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.animation_particles(self.player.rect.center, [self.visible_sprites], attack_type)

    def enemy_death_effect(self, pos, enemy_type):
        self.animation_player.animation_particles(pos, [self.visible_sprites], enemy_type)

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.visible_sprites.enemy_update(self.player)
        self.player_attack()
        self.ui.display(self.player)


# Customizing the Group class
# to create a camera and
# add depth effect
class YSortCameraGroup(pygame.sprite.Group):
    
    def __init__(self):
        super().__init__()

        self.display_surface = pygame.display.get_surface()

        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # Creating the floor
        self.floor_surf = pygame.image.load('../graphics/tilemap/ground.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft = (0, 0))
    
    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # Drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset

            self.display_surface.blit(sprite.image, offset_pos)

    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']

        for enemy in enemy_sprites:
            enemy.enemy_update(player)
