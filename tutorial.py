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
        "Déplacer",
        "Clique une unité : les cases possibles s'affichent. Clique une case bleue pour avancer.",
    ),
    (
        "Villes et production",
        "Clique une ville pour recruter. Le panneau du bas ne montre que ce que cette case peut faire.",
    ),
    (
        "Mer",
        "La plage se marche à pied. Clique l'eau cyan pour embarquer, le vert pour débarquer.",
    ),
    (
        "Fin de tour",
        "Quand tes unités ont bougé : bouton vert en bas à droite, ou Espace. Échap : pause.",
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
        panel_w = min(640, WINDOW_WIDTH - 40)
        panel_h = 200
        panel_x = (WINDOW_WIDTH - panel_w) // 2
        panel_y = WINDOW_HEIGHT // 2 - panel_h // 2
        pygame.draw.rect(surface, (35, 38, 48), (panel_x, panel_y, panel_w, panel_h), border_radius=12)
        pygame.draw.rect(surface, (90, 100, 120), (panel_x, panel_y, panel_w, panel_h), 2, border_radius=12)
        title_font = pygame.font.Font(None, 34)
        body_font = pygame.font.Font(None, 24)
        hint_font = pygame.font.Font(None, 22)
        title, body = TUTORIAL_STEPS[self.step]
        surface.blit(title_font.render(title, True, (255, 220, 120)), title_font.render(title, True, (255, 220, 120)).get_rect(center=(WINDOW_WIDTH // 2, panel_y + 42)))
        surface.blit(body_font.render(body, True, (230, 230, 230)), body_font.render(body, True, (230, 230, 230)).get_rect(center=(WINDOW_WIDTH // 2, panel_y + 100)))
        hint = hint_font.render(
            f"Étape {self.step + 1}/{len(TUTORIAL_STEPS)} — Clic ou Entrée pour continuer",
            True,
            (180, 180, 190),
        )
        surface.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, panel_y + panel_h - 28)))
