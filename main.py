import sys
import pygame

from settings import *

from level import Level

class Game:
    
    def __init__(self):
        self.initialize_game()

    def initialize_game(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Yuusha")
        self.clock = pygame.time.Clock()

        self.level = Level()

        # Background music
        self.bg_music = pygame.mixer.Sound('../audio/main.ogg')
        self.bg_music.set_volume(0.08)
        self.bg_music.play(loops = -1)

    def fade_out(self):
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0, 0, 0))
        for alpha in range(0, 255):  # Adjust the step value for speed of fade
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(20)  # Adjust the delay for smoothness

    def game_over_screen(self):
        self.fade_out()
        self.screen.fill('black')

        # Display a game over message
        game_over_font = pygame.font.Font(UI_FONT, 74)
        game_over_surf = game_over_font.render("Game Over", False, (255, 0, 0))
        game_over_rect = game_over_surf.get_rect(center=(WIDTH//2, HEIGHT//3))
        self.screen.blit(game_over_surf, game_over_rect)

        option_font = pygame.font.Font(UI_FONT, 50)
        quit_surf = option_font.render("QUIT (Q)", False, (255, 0, 0))
        quit_rect = quit_surf.get_rect(center = game_over_rect.center + pygame.math.Vector2(0, 120))
        self.screen.blit(quit_surf, quit_rect)

        # option_font = pygame.font.Font(UI_FONT, 50)
        restart_surf = option_font.render("RESTART (R)", False, (0, 255, 0))
        restart_rect = restart_surf.get_rect(center = game_over_rect.center + pygame.math.Vector2(0, 240))
        self.screen.blit(restart_surf, restart_rect)

        pygame.display.update()

        # Waiting for user input to restart the game
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                    if event.key == pygame.K_r:  # Press 'R' to restart the game
                        waiting = False
                        self.initialize_game()
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:
                        self.level.toggle_menu()
                
            if self.level.game_over():
                self.bg_music.stop()
                self.game_over_screen()
            else:
                self.screen.fill(WATER_COLOR)
                self.level.run()

            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()