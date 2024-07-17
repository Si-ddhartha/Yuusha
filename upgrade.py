import pygame

from settings import *

class Upgrade:

    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.attributes_len = len(self.player.stats)
        self.attributes_name = list(self.player.stats.keys())
        self.max_values = list(self.player.max_stats.values())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # Selection system
        self.selection_index = 0
        self.selection_time = None
        self.selection_interval = 200
        self.can_switch = True

        # Item box 
        self.height = HEIGHT * 0.8
        self.width = WIDTH // (self.attributes_len + 1)
        self.create_items()

    def input(self):
        keys = pygame.key.get_pressed()

        if self.can_switch:
            if keys[pygame.K_RIGHT]:
                self.selection_index += 1
                self.selection_time = pygame.time.get_ticks()
                self.can_switch = False

                self.selection_index = min(self.attributes_len - 1, self.selection_index)
            
            elif keys[pygame.K_LEFT]:
                self.selection_index -= 1
                self.selection_time = pygame.time.get_ticks()
                self.can_switch = False

                self.selection_index = max(0, self.selection_index)
                
            if keys[pygame.K_SPACE]:
                self.can_switch = False 
                self.selection_time = pygame.time.get_ticks()
                self.item_list[self.selection_index].change_value(self.player)

    def selection_cooldown(self):
        if not self.can_switch:
            current_time = pygame.time.get_ticks()

            if current_time - self.selection_time >= self.selection_interval:
                self.can_switch = True

    def create_items(self):
        self.item_list = []

        top = HEIGHT * 0.1
        left_increment = WIDTH // self.attributes_len

        for i in range(self.attributes_len):
            left = (i * left_increment) + (left_increment - self.width) // 2

            item = Item(left, top, self.width, self.height, i, self.font)
            self.item_list.append(item)

    def display_menu(self):
        self.input()
        self.selection_cooldown()

        for index, item in enumerate(self.item_list):
            # Attributes
            name = self.attributes_name[index].split('_')[1] if 'max' in self.attributes_name[index] else self.attributes_name[index]
            value = list(self.player.stats.values())[index]
            max_value = self.max_values[index]
            cost = list(self.player.upgrade_cost.values())[index]

            item.display(self.display_surface, self.selection_index, name, value, max_value, int(cost))


class Item:

    def __init__(self, left, top, width, height, index, font):
        self.rect = pygame.Rect(left, top, width, height)
        self.index = index
        self.font = font

    def display_text(self, surface, name, cost, selected):
        text_color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

        name_surf = self.font.render(name, False, text_color)
        name_rect = name_surf.get_rect(midtop = self.rect.midtop + pygame.math.Vector2(0, 20))

        cost_surf = self.font.render(str(cost), False, text_color)
        cost_rect = cost_surf.get_rect(midbottom = self.rect.midbottom - pygame.math.Vector2(0, 20))

        surface.blit(name_surf, name_rect)
        surface.blit(cost_surf, cost_rect)

    def display_bar(self, surface, value, max_value, selected):
        top = self.rect.midtop + pygame.math.Vector2(0, 60)
        bottom = self.rect.midbottom - pygame.math.Vector2(0, 60)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR

        full_height = bottom[1] - top[1]
        relative_val = (value / max_value) * full_height
        value_rect = pygame.Rect(top[0] - 15, bottom[1] - relative_val, 30, 10)

        pygame.draw.line(surface, color, top, bottom, 5)
        pygame.draw.rect(surface, color, value_rect)

    def display(self, surface, selection_num, name, val, max_val, cost):
        if self.index == selection_num:
            pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
        
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)

        pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        self.display_text(surface, name, cost, self.index == selection_num)
        self.display_bar(surface, val, max_val, self.index == selection_num)

    def change_value(self, player):
        attribute_name = list(player.stats.keys())[self.index]
        attribute_name_for_cost = attribute_name.split('_')[1] if 'max' in attribute_name else attribute_name
        attribute_name_for_max = 'max_' + attribute_name if 'max' not in attribute_name else attribute_name

        if player.exp >= player.upgrade_cost[attribute_name_for_cost] and player.stats[attribute_name] < player.max_stats[attribute_name_for_max]:
            player.exp -= player.upgrade_cost[attribute_name_for_cost]
            player.stats[attribute_name] *= 1.2
            player.upgrade_cost[attribute_name_for_cost] *= 1.4

        player.stats[attribute_name] = min(player.stats[attribute_name], player.max_stats[attribute_name_for_max])
