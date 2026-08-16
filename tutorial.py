"""Tutoriel au premier lancement."""

import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from settings import load_settings, save_settings
from theme import INK, INK_SOFT, draw_panel, load_font, wrap_text

TUTORIAL_STEPS = [
    (
        "Ton palais est fondé",
        "Gagne en prenant toutes les capitales, ou en étant le dernier royaume.",
    ),
    (
        "Tes unités",
        "Clique une armée. Les cases vertes bordées, c'est ta portée. Survole : le fantôme montre l'arrêt.",
    ),
    (
        "La boucle du tour",
        "N passe à l'unité suivante. Quand plus personne n'a de mouvement, Fin de tour clignote. Espace termine le tour.",
    ),
    (
        "Villes",
        "Clique une ville pour produire (lancier, spadassin, arbalète, cavalerie, catapulte). Une ville ennemie a des murs et une garnison : on ne la prend pas en marchant dessus.",
    ),
]


class Tutorial:
    def __init__(self):
        self.active = False
        self.step = 0

    def should_show(self):
        return not load_settings().get("tutorial_done", False)

    def mark_done(self):
        data = load_settings()
        data["tutorial_done"] = True
        save_settings(data)
        self.active = False

    def start(self):
        if self.should_show():
            self.active = True
            self.step = 0

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            if self.step >= len(TUTORIAL_STEPS) - 1:
                self.mark_done()
            else:
                self.step += 1
            return True
        return False

    def draw(self, surface):
        if not self.active:
            return
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((40, 24, 12, 170))
        surface.blit(overlay, (0, 0))
        panel_w = min(620, WINDOW_WIDTH - 40)
        panel_h = 220
        panel_x = (WINDOW_WIDTH - panel_w) // 2
        panel_y = WINDOW_HEIGHT // 2 - panel_h // 2
        rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        draw_panel(surface, rect)
        title_font = load_font(28, bold=True)
        body_font = load_font(20)
        hint_font = load_font(16)
        title, body = TUTORIAL_STEPS[self.step]
        title_surf = title_font.render(title, True, (120, 48, 28))
        surface.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 46)))
        wrapped = wrap_text(body_font, body, panel_w - 48)
        text_y = panel_y + 88
        for line in wrapped:
            line_surf = body_font.render(line, True, INK)
            surface.blit(line_surf, line_surf.get_rect(center=(WINDOW_WIDTH // 2, text_y)))
            text_y += 26
        hint = hint_font.render(
            f"{self.step + 1}/{len(TUTORIAL_STEPS)}   Clic ou Entrée",
            True,
            INK_SOFT,
        )
        surface.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, panel_y + panel_h - 32)))
