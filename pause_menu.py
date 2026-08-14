"""Menu pause et écran des réglages en jeu."""

import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, GRID_COLS, CELL_SIZE
from menu import Button
from theme import INK, INK_SOFT, draw_panel, load_font

MAP_WIDTH = GRID_COLS * CELL_SIZE
from settings import (
    AI_SPEED_DELAYS_MS,
    DIFFICULTY_CONFIG,
    cycle_value,
    load_settings,
    save_settings,
)


class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.open = False
        self.submenu = "main"
        self.settings = load_settings()
        self.font_title = load_font(36, bold=True)
        self.font_body = load_font(22)
        self._build_buttons()

    def _build_buttons(self):
        bw, bh = 280, 44
        cx = MAP_WIDTH // 2 - bw // 2
        y = WINDOW_HEIGHT // 2 - 90

        self.btn_resume = Button(cx, y, bw, bh, "Reprendre")
        self.btn_settings = Button(cx, y + 52, bw, bh, "Réglages")
        self.btn_save = Button(cx, y + 104, bw, bh, "Sauvegarder")
        self.btn_quit = Button(cx, y + 156, bw, bh, "Menu principal")

        self.btn_back = Button(cx, WINDOW_HEIGHT - 90, bw, bh, "Retour")
        self.btn_vol_down = Button(cx + 20, 280, 60, 40, "-")
        self.btn_vol_up = Button(cx + bw - 80, 280, 60, 40, "+")
        self.btn_speed = Button(cx, 340, bw, 40, "")
        self.btn_difficulty = Button(cx, 390, bw, 40, "")

    def toggle(self):
        self.open = not self.open
        if self.open:
            self.submenu = "main"
            self.settings = load_settings()
        return self.open

    def close(self):
        self.open = False
        self.submenu = "main"

    def apply_to_game(self, game):
        self.settings = save_settings(self.settings)
        game.settings = dict(self.settings)
        game.audio.set_volume(self.settings["volume"])
        game.difficulty_cfg = DIFFICULTY_CONFIG.get(
            self.settings.get("difficulty", "normal"),
            DIFFICULTY_CONFIG["normal"],
        )

    def leave_settings(self, game):
        self.submenu = "main"
        self.apply_to_game(game)

    def get_ai_delay_ms(self):
        return AI_SPEED_DELAYS_MS.get(self.settings["ai_speed"], 1000)

    def handle_event(self, event, game):
        if not self.open:
            return None

        if self.submenu == "settings":
            return self._handle_settings(event, game)

        if self.btn_resume.handle_event(event):
            self.close()
            return "resume"
        if self.btn_settings.handle_event(event):
            self.submenu = "settings"
            return None
        if self.btn_save.handle_event(event):
            return "save"
        if self.btn_quit.handle_event(event):
            return "quit_menu"
        return "blocked"

    def _handle_settings(self, event, game):
        if self.btn_back.handle_event(event):
            self.leave_settings(game)
            return None
        elif self.btn_vol_down.handle_event(event):
            self.settings["volume"] = max(0.0, round(self.settings["volume"] - 0.1, 2))
            self.apply_to_game(game)
            game.audio.play("click")
        elif self.btn_vol_up.handle_event(event):
            self.settings["volume"] = min(1.0, round(self.settings["volume"] + 0.1, 2))
            self.apply_to_game(game)
            game.audio.play("click")
        elif self.btn_speed.handle_event(event):
            self.settings["ai_speed"] = cycle_value(
                self.settings["ai_speed"], list(AI_SPEED_DELAYS_MS.keys())
            )
            self.apply_to_game(game)
            game.audio.play("click")
        elif self.btn_difficulty.handle_event(event):
            self.settings["difficulty"] = cycle_value(
                self.settings["difficulty"], list(DIFFICULTY_CONFIG.keys())
            )
            self.apply_to_game(game)
            game.audio.play("click")
        return "blocked"

    def draw(self, game):
        if not self.open:
            return

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((40, 24, 12, 180))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(MAP_WIDTH // 2 - 200, 70, 400, WINDOW_HEIGHT - 140)
        draw_panel(self.screen, panel)

        title = self.font_title.render("Pause", True, (120, 48, 28))
        self.screen.blit(title, title.get_rect(center=(MAP_WIDTH // 2, 120)))

        if self.submenu == "main":
            self.btn_resume.draw(self.screen, self.font_body)
            self.btn_settings.draw(self.screen, self.font_body)
            self.btn_save.draw(self.screen, self.font_body)
            self.btn_quit.draw(self.screen, self.font_body)
            hint = self.font_body.render("Échap : reprendre", True, INK_SOFT)
            self.screen.blit(hint, hint.get_rect(center=(MAP_WIDTH // 2, WINDOW_HEIGHT - 40)))
            return

        settings_title = self.font_title.render("Réglages", True, (120, 48, 28))
        self.screen.blit(settings_title, settings_title.get_rect(center=(MAP_WIDTH // 2, 170)))

        vol_pct = int(self.settings["volume"] * 100)
        vol_line = self.font_body.render(f"Volume: {vol_pct}%", True, INK)
        self.screen.blit(vol_line, (MAP_WIDTH // 2 - 140, 250))
        self.btn_vol_down.draw(self.screen, self.font_body)
        self.btn_vol_up.draw(self.screen, self.font_body)

        speed_labels = {
            "instant": "Instantané",
            "fast": "Rapide",
            "normal": "Normal",
            "slow": "Lent",
        }
        speed_key = self.settings.get("ai_speed", "normal")
        self.btn_speed.text = f"Vitesse IA: {speed_labels.get(speed_key, speed_key)}"
        self.btn_speed.draw(self.screen, self.font_body)

        diff_labels = {"easy": "Facile", "normal": "Normal", "hard": "Difficile"}
        diff_key = self.settings.get("difficulty", "normal")
        self.btn_difficulty.text = (
            f"Difficulté (prochaine partie) : {diff_labels.get(diff_key, diff_key)}"
        )
        self.btn_difficulty.draw(self.screen, self.font_body)

        note = self.font_body.render(
            "N : unité suivante   Espace : fin de tour", True, INK
        )
        self.screen.blit(note, note.get_rect(center=(MAP_WIDTH // 2, 450)))

        self.btn_back.draw(self.screen, self.font_body)
