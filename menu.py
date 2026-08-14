import math
import pygame
from constants import *
from settings import load_settings, save_settings, cycle_value, DIFFICULTY_CONFIG
from theme import (
    CREAM,
    GOLD,
    GOLD_BRIGHT,
    INK,
    PARCHMENT,
    WOOD,
    WOOD_DARK,
    WOOD_LIGHT,
    draw_bevel_rect,
    load_font,
)


class Button:
    def __init__(self, x, y, width, height, text, color=None, hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color or WOOD
        self.hover_color = hover_color or WOOD_LIGHT
        self.is_hovered = False

    def draw(self, surface, font):
        fill = self.hover_color if self.is_hovered else self.color
        draw_bevel_rect(surface, self.rect, fill, GOLD_BRIGHT, WOOD_DARK, 2)
        pygame.draw.rect(surface, GOLD, self.rect, 1)
        text_surface = font.render(self.text, True, CREAM)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = load_font(54, bold=True)
        self.font_button = load_font(28, bold=True)
        self.font_small = load_font(20)
        self.state = "main"
        self.selected_mode = None

        button_width = 320
        button_height = 48
        button_x = (WINDOW_WIDTH - button_width) // 2
        start_y = 230

        self.btn_new_game = Button(button_x, start_y, button_width, button_height, "Nouvelle partie")
        self.btn_load_game = Button(button_x, start_y + 58, button_width, button_height, "Charger une partie")
        self.btn_quit = Button(button_x, start_y + 116, button_width, button_height, "Quitter")
        self.btn_solo = Button(button_x, start_y, button_width, button_height, "Solo, un royaume")
        self.btn_godgame = Button(button_x, start_y + 58, button_width, button_height, "Dieu, tous les royaumes")
        self.btn_back = Button(button_x, start_y + 116, button_width, button_height, "Retour")
        self.btn_difficulty = Button(button_x, start_y + 174, button_width, 42, "")
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
        t = pygame.time.get_ticks() / 1000.0
        self.screen.fill(WOOD_DARK)
        pygame.draw.rect(self.screen, PARCHMENT, (24, 24, WINDOW_WIDTH - 48, WINDOW_HEIGHT - 48))
        for x in range(24, WINDOW_WIDTH - 24, 36):
            pygame.draw.line(self.screen, (214, 196, 158), (x, 24), (x, WINDOW_HEIGHT - 24))
        for y in range(24, WINDOW_HEIGHT - 24, 36):
            pygame.draw.line(self.screen, (214, 196, 158), (24, y), (WINDOW_WIDTH - 24, y))
        islands = [
            (int(WINDOW_WIDTH * 0.28), int(WINDOW_HEIGHT * 0.30), Country.RED),
            (int(WINDOW_WIDTH * 0.70), int(WINDOW_HEIGHT * 0.26), Country.BLUE),
            (int(WINDOW_WIDTH * 0.30), int(WINDOW_HEIGHT * 0.72), Country.GREEN),
            (int(WINDOW_WIDTH * 0.72), int(WINDOW_HEIGHT * 0.70), Country.YELLOW),
            (int(WINDOW_WIDTH * 0.50), int(WINDOW_HEIGHT * 0.50), Country.ORANGE),
        ]
        for x, y, country in islands:
            bob = int(3 * math.sin(t * 0.7 + x))
            pygame.draw.ellipse(self.screen, (48, 92, 128), (x - 86, y - 48 + bob, 172, 96))
            pygame.draw.ellipse(self.screen, (92, 128, 64), (x - 70, y - 36 + bob, 140, 72))
            pygame.draw.ellipse(self.screen, COUNTRY_COLORS[country], (x - 14, y - 8 + bob, 28, 18))
        frame = pygame.Rect(18, 18, WINDOW_WIDTH - 36, WINDOW_HEIGHT - 36)
        pygame.draw.rect(self.screen, WOOD, frame.inflate(10, 10), 10)
        pygame.draw.rect(self.screen, GOLD, frame, 3)

    def draw(self):
        self._draw_backdrop()
        title = self.font_title.render("The World Is Ours", True, WOOD_DARK)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2 + 2, 92)))
        title = self.font_title.render("The World Is Ours", True, (120, 48, 28))
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 90)))
        if self.state == "main":
            subtitle = self.font_small.render("Cinq royaumes, une mer.", True, INK)
        else:
            subtitle = self.font_small.render("Choisis comment gouverner.", True, INK)
        self.screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 148)))
        hint = self.font_small.render("Prends toutes les capitales, ou reste le dernier debout.", True, INK)
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, 178)))

        if self.state == "main":
            self.btn_new_game.draw(self.screen, self.font_button)
            self.btn_load_game.draw(self.screen, self.font_button)
            self.btn_quit.draw(self.screen, self.font_button)
            if self.load_error:
                err = self.font_small.render(self.load_error, True, (140, 36, 28))
                self.screen.blit(err, err.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 56)))
        elif self.state == "mode_select":
            labels = {"easy": "Facile", "normal": "Normal", "hard": "Difficile"}
            diff = self.settings.get("difficulty", "normal")
            self.btn_difficulty.text = f"Difficulté : {labels.get(diff, diff)}"
            self.btn_difficulty.draw(self.screen, self.font_button)
            self.btn_solo.draw(self.screen, self.font_button)
            self.btn_godgame.draw(self.screen, self.font_button)
            self.btn_back.draw(self.screen, self.font_button)
        pygame.display.flip()
