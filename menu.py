import pygame
from constants import *
from settings import load_settings, save_settings, cycle_value, DIFFICULTY_CONFIG

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=8)
        
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Use click position directly so a click works
            # even if no prior MOUSEMOTION was emitted.
            if self.rect.collidepoint(event.pos):
                return True
        return False

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # État du menu
        self.state = "main"  # main, mode_select
        self.selected_mode = None
        
        # Boutons menu principal
        button_width = 300
        button_height = 60
        button_x = (WINDOW_WIDTH - button_width) // 2
        start_y = 300
        
        self.btn_new_game = Button(
            button_x, start_y, button_width, button_height,
            "Nouvelle Partie", (41, 128, 185), (52, 152, 219)
        )
        
        self.btn_load_game = Button(
            button_x, start_y + 80, button_width, button_height,
            "Charger Partie", (39, 174, 96), (46, 204, 113)
        )
        
        self.btn_quit = Button(
            button_x, start_y + 160, button_width, button_height,
            "Quitter", (192, 57, 43), (231, 76, 60)
        )
        
        # Boutons sélection de mode
        self.btn_solo = Button(
            button_x, start_y, button_width, button_height,
            "Solo (vs IA)", (142, 68, 173), (155, 89, 182)
        )
        
        self.btn_godgame = Button(
            button_x, start_y + 80, button_width, button_height,
            "God Game", (230, 126, 34), (243, 156, 18)
        )
        
        self.btn_back = Button(
            button_x, start_y + 160, button_width, button_height,
            "Retour", (127, 140, 141), (149, 165, 166)
        )
        self.btn_difficulty = Button(
            button_x, start_y + 240, button_width, 44,
            "", (90, 110, 150), (105, 130, 170)
        )
        self.settings = load_settings()
        self.load_error = ""

    def handle_event(self, event):
        if self.state == "main":
            if self.btn_new_game.handle_event(event):
                self.state = "mode_select"
                self.settings = load_settings()
                return None
            
            if self.btn_load_game.handle_event(event):
                self.load_error = ""
                return "load"
            
            if self.btn_quit.handle_event(event):
                return "quit"
        
        elif self.state == "mode_select":
            if self.btn_difficulty.handle_event(event):
                self.settings["difficulty"] = cycle_value(
                    self.settings.get("difficulty", "normal"),
                    list(DIFFICULTY_CONFIG.keys()),
                )
                self.settings = save_settings(self.settings)
                return None

            if self.btn_solo.handle_event(event):
                return "start_solo"
            
            if self.btn_godgame.handle_event(event):
                return "start_godgame"
            
            if self.btn_back.handle_event(event):
                self.state = "main"
                return None
        
        return None
    
    def _draw_backdrop(self):
        import math
        t = pygame.time.get_ticks() / 1000.0
        self.screen.fill((14, 32, 58))
        for i in range(18):
            y = int((i * 58 + t * 28) % (WINDOW_HEIGHT + 40)) - 20
            shade = 28 + (i % 4) * 6
            pygame.draw.line(self.screen, (shade, 70 + i % 5, 110), (0, y), (WINDOW_WIDTH, y + 8), 2)
        islands = [
            (180, 220, Country.RED),
            (780, 180, Country.BLUE),
            (260, 720, Country.GREEN),
            (860, 680, Country.YELLOW),
            (520, 420, Country.ORANGE),
        ]
        for x, y, country in islands:
            bob = int(6 * math.sin(t * 1.1 + x))
            pygame.draw.ellipse(self.screen, (48, 120, 62), (x - 70, y - 40 + bob, 140, 80))
            pygame.draw.ellipse(self.screen, COUNTRY_COLORS[country], (x - 18, y - 10 + bob, 36, 24))
        veil = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        veil.fill((8, 10, 16, 120))
        self.screen.blit(veil, (0, 0))

    def draw(self):
        self._draw_backdrop()
        title = self.font_title.render("The World Is Ours", True, (255, 215, 0))
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 150)))
        if self.state == "main":
            subtitle = self.font_small.render("Un jeu de conquête médiéval", True, (200, 200, 200))
        else:
            subtitle = self.font_small.render("Choisissez votre mode de jeu", True, (200, 200, 200))
        self.screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 220)))

        if self.state == "main":
            self.btn_new_game.draw(self.screen, self.font_button)
            self.btn_load_game.draw(self.screen, self.font_button)
            self.btn_quit.draw(self.screen, self.font_button)
            if self.load_error:
                err = self.font_small.render(self.load_error, True, (240, 160, 140))
                self.screen.blit(err, err.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)))
        elif self.state == "mode_select":
            labels = {"easy": "Facile", "normal": "Normal", "hard": "Difficile"}
            diff = self.settings.get("difficulty", "normal")
            self.btn_difficulty.text = f"Difficulté : {labels.get(diff, diff)}"
            self.btn_difficulty.draw(self.screen, self.font_button)
            self.btn_solo.draw(self.screen, self.font_button)
            self.btn_godgame.draw(self.screen, self.font_button)
            self.btn_back.draw(self.screen, self.font_button)
            hint = self.font_small.render(
                "Rouge : lames  ·  Bleu : mer  ·  Vert : forêts  ·  Jaune : or  ·  Orange : cavalerie",
                True,
                (170, 175, 185),
            )
            self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40)))
        pygame.display.flip()