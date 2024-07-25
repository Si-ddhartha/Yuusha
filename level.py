import sys
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
from upgrade import Upgrade
from flame import Flame

class Level:

    def __init__(self):
        # Get the display surface
        self.display_surface = pygame.display.get_surface()

        self.game_paused = False

        # Sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # Attack sprites
        self.current_attack = None

        self.create_map()

        # UI setup
        self.ui = UI()
        self.upgrade = Upgrade(self.player)

        # Particles
        self.animation_player = AnimationPlayer()

        # Magic
        self.magic_player = MagicPlayer(self.animation_player)
    
    def show_controls_screen(self):
        self.display_surface.fill((0, 0, 0))

        basic_controls = [
            "Move: Arrow keys or WASD",
            "Attack: Space",
            "Switch Weapon: Q",
            "Magic (Flame or Heal): F",
            "Switch Magic: E"
        ]

        upgrade_menu_controls = [
            "Toggle Upgrade Menu: U",
            "Select item: Left or Right key",
            "Upgrade selected item: Space"
        ]

        main_heading_font = pygame.font.Font(UI_FONT, 50)
        main_heading_surf = main_heading_font.render("CONTROLS", False, (255, 255, 255))
        main_heading_rect = main_heading_surf.get_rect(center = (WIDTH//2, 70))
        self.display_surface.blit(main_heading_surf, main_heading_rect)

        # Draw line beneath the main heading
        underline_y = main_heading_rect.bottom - 2
        pygame.draw.line(self.display_surface, (255, 255, 255), (main_heading_rect.left, underline_y), (main_heading_rect.right, underline_y), 5)

        item_font = pygame.font.Font(UI_FONT, 30)
        for i, text in enumerate(basic_controls):
            text_surf = item_font.render(text, False, (0, 0, 255))
            text_rect = text_surf.get_rect(topleft = (50, (150 + (i * 100))))
            self.display_surface.blit(text_surf, text_rect)

        for i, text in enumerate(upgrade_menu_controls):
            text_surf = item_font.render(text, False, (0, 0, 255))
            text_rect = text_surf.get_rect(topleft = (WIDTH // 2, (150 + (i * 100))))
            self.display_surface.blit(text_surf, text_rect)

        footer_font = pygame.font.Font(UI_FONT, 20)
        footer_surf = footer_font.render("Press X to start game", False, (255, 255, 255))
        footer_rect = footer_surf.get_rect(center = (WIDTH//2, HEIGHT - 50))
        self.display_surface.blit(footer_surf, footer_rect)

        pygame.display.update()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x: # Press X to start game
                        waiting = False
   
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
                            elif col == '22': # Blue flame
                                Flame((x, y), [self.visible_sprites, self.obstacle_sprites], 'object')
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
                                        self.enemy_death_effect,
                                        self.get_exp)

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

    def get_exp(self, exp_amount):
        self.player.exp += exp_amount

    def toggle_menu(self):
        self.game_paused = not self.game_paused

    def game_over(self):
        return self.player.health <= 0

    def run(self):
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)

        if self.game_paused:
            self.upgrade.display_menu()
        
        else:
            self.visible_sprites.update()
            self.visible_sprites.enemy_update(self.player)
            self.player_attack()


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
