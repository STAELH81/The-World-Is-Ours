"""Tutoriel au premier lancement."""

import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from settings import load_settings, save_settings

TUTORIAL_STEPS = [
    (
        "Bienvenue dans The World Is Ours",
        "Conquiers les capitales ennemies ou sois le dernier royaume debout.",
    ),
    (
        "Selection",
        "Clique une case pour voir ses infos et les actions disponibles.",
    ),
    (
        "Economie",
        "Recrute dans tes villes/capitales, construis des villes et des ponts.",
    ),
    (
        "Armee",
        "Deplace tes unites, fortifie-les ou tire a distance (arbaletriers).",
    ),
    (
        "Fin de tour",
        "Quand tu as fini, clique « Fin de tour ». La partie est sauvegardee automatiquement.",
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
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        panel_w = min(560, WINDOW_WIDTH - 40)
        panel_h = 180
        panel_x = (WINDOW_WIDTH - panel_w) // 2
        panel_y = WINDOW_HEIGHT // 2 - panel_h // 2
        pygame.draw.rect(surface, (35, 38, 48), (panel_x, panel_y, panel_w, panel_h), border_radius=12)
        pygame.draw.rect(surface, (90, 100, 120), (panel_x, panel_y, panel_w, panel_h), 2, border_radius=12)

        title_font = pygame.font.Font(None, 34)
        body_font = pygame.font.Font(None, 26)
        hint_font = pygame.font.Font(None, 22)

        title, body = TUTORIAL_STEPS[self.step]
        title_surf = title_font.render(title, True, (255, 220, 120))
        body_surf = body_font.render(body, True, (230, 230, 230))
        hint = hint_font.render(
            f"Etape {self.step + 1}/{len(TUTORIAL_STEPS)} — Clic ou Entree pour continuer",
            True,
            (180, 180, 190),
        )

        surface.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 42)))
        surface.blit(body_surf, body_surf.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 95)))
        surface.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, panel_y + panel_h - 28)))
