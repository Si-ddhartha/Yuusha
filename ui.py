import pygame

from settings import *

class UI:

    def __init__(self):
        # General
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # Bar setup
        self.health_bar = pygame.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.energy_bar = pygame.Rect(10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT)

        # Pre-loading weapons graphics
        self.weapon_graphics = []
        for weapon in weapon_data.values():
            path = weapon['graphic']
            weapon = pygame.image.load(path).convert_alpha()
            self.weapon_graphics.append(weapon)

    def draw_bar(self, bg_rect, curr_amount, max_amount, color):
        # Draw bg
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        # Convert int stats to pixels
        ratio = curr_amount / max_amount
        curr_width = bg_rect.width * ratio
        curr_rect = bg_rect.copy()
        curr_rect.width = curr_width

        # Draw the bar
        pygame.draw.rect(self.display_surface, color, curr_rect)

        # Draw the border
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def draw_exp(self, curr_exp):
        text_surf = self.font.render(str(int(curr_exp)), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(topright = (WIDTH - 20, 20))

        pygame.draw.rect(self.display_surface, UI_BG_COLOR ,text_rect.inflate(20, 20))
        self.display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR ,text_rect.inflate(20, 20), 3)

    def draw_selection_box(self, left, top, is_switching):
        bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)

        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        if is_switching:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
        
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

        return bg_rect
    
    def draw_weapon(self, curr_weapon_index, is_switching):
        bg_rect = self.draw_selection_box(10, 625 ,is_switching)

        weapon_surf = self.weapon_graphics[curr_weapon_index]
        weapon_rect = weapon_surf.get_rect(center = bg_rect.center)

        self.display_surface.blit(weapon_surf, weapon_rect)

    def display(self, player):
        self.draw_bar(self.health_bar, player.health, player.stats['max_health'], HEALTH_COLOR)
        self.draw_bar(self.energy_bar, player.energy, player.stats['max_energy'], ENERGY_COLOR)

        self.draw_exp(player.exp)

        self.draw_weapon(player.weapon_index, not player.can_switch_weapon) # Weapon box
        # self.draw_selection_box(80, 634) # Magic box
