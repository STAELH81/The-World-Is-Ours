"""Marche des unités, bannières de tour et textes flottants."""

import pygame
from constants import (
    CELL_SIZE,
    COUNTRY_NAMES,
    Country,
    GRID_COLS,
    GRID_ROWS,
    MAP_ORIGIN_X,
    MAP_ORIGIN_Y,
    MAP_PIXEL_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    cell_screen_pos,
)
from cell import draw_army_at


class Effects:
    def __init__(self):
        self.walk = None
        self.banner = None
        self.floaters = []
        self._font = None
        self._title_font = None

    def _fonts(self):
        from theme import load_font

        if self._font is None:
            self._font = load_font(18)
            self._title_font = load_font(28, bold=True)
        return self._font, self._title_font

    def is_busy(self):
        return self.walk is not None

    def hidden_army_cells(self):
        if not self.walk:
            return set()
        return {self.walk["origin"]}

    def start_walk(self, origin_cell, path_cells, army, on_done, ticks_per_cell=7):
        if not path_cells:
            if on_done:
                on_done()
            return
        coords = [(origin_cell.x, origin_cell.y)] + [(cell.x, cell.y) for cell in path_cells]
        self.walk = {
            "coords": coords,
            "army": army,
            "origin": (origin_cell.x, origin_cell.y),
            "on_done": on_done,
            "t": 0,
            "ticks_per_cell": max(3, ticks_per_cell),
            "segment": 0,
        }

    def show_banner(self, text, ttl=80):
        self.banner = {"text": text, "ttl": ttl, "max_ttl": ttl}

    def float_text(self, cell_x, cell_y, text, color, ttl=48):
        self.floaters.append(
            {
                "px": MAP_ORIGIN_X + cell_x * CELL_SIZE + CELL_SIZE // 2,
                "py": MAP_ORIGIN_Y + cell_y * CELL_SIZE + 8,
                "text": text,
                "color": color,
                "ttl": ttl,
                "max_ttl": ttl,
            }
        )

    def clear(self):
        self.walk = None
        self.banner = None
        self.floaters.clear()

    def update(self):
        if self.walk:
            self.walk["t"] += 1
            if self.walk["t"] >= self.walk["ticks_per_cell"]:
                self.walk["t"] = 0
                self.walk["segment"] += 1
                if self.walk["segment"] >= len(self.walk["coords"]) - 1:
                    done = self.walk["on_done"]
                    self.walk = None
                    if done:
                        done()
        if self.banner:
            self.banner["ttl"] -= 1
            if self.banner["ttl"] <= 0:
                self.banner = None
        for floater in self.floaters:
            floater["ttl"] -= 1
            floater["py"] -= 0.55
        self.floaters = [floater for floater in self.floaters if floater["ttl"] > 0]

    def draw(self, screen):
        font, title_font = self._fonts()
        if self.walk:
            coords = self.walk["coords"]
            last = len(coords) - 2
            seg = min(self.walk["segment"], max(0, last))
            start = coords[seg]
            end = coords[min(seg + 1, len(coords) - 1)]
            k = self.walk["t"] / self.walk["ticks_per_cell"]
            px = MAP_ORIGIN_X + (start[0] + (end[0] - start[0]) * k) * CELL_SIZE
            py = MAP_ORIGIN_Y + (start[1] + (end[1] - start[1]) * k) * CELL_SIZE
            draw_army_at(screen, int(px), int(py), self.walk["army"])
        if self.banner:
            from theme import GOLD_BRIGHT, PARCHMENT, WOOD, draw_bevel_rect

            width = MAP_PIXEL_WIDTH
            rect = pygame.Rect(40, WINDOW_HEIGHT // 2 - 70, width - 80, 56)
            draw_bevel_rect(screen, rect, WOOD, GOLD_BRIGHT, (40, 24, 12), 2)
            pygame.draw.rect(screen, PARCHMENT, rect.inflate(-8, -8))
            text = title_font.render(self.banner["text"], True, (48, 28, 14))
            screen.blit(text, text.get_rect(center=rect.center))
        for floater in self.floaters:
            fade = max(40, int(255 * floater["ttl"] / floater["max_ttl"]))
            surf = font.render(floater["text"], True, floater["color"])
            surf.set_alpha(fade)
            screen.blit(surf, surf.get_rect(center=(int(floater["px"]), int(floater["py"]))))


def draw_end_recap(screen, game):
    from theme import GOLD, INK, PARCHMENT, draw_panel, load_font, wrap_text

    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill((40, 24, 12, 200))
    screen.blit(overlay, (0, 0))

    panel_w, panel_h = min(560, WINDOW_WIDTH - 40), 380
    panel_x = (WINDOW_WIDTH - panel_w) // 2
    panel_y = (WINDOW_HEIGHT - panel_h) // 2
    rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
    draw_panel(screen, rect)

    title_font = load_font(32, bold=True)
    body = load_font(20)
    small = load_font(18)

    title = game.game_over_message or "Partie terminée"
    title_surf = title_font.render(title, True, (120, 48, 28))
    screen.blit(title_surf, title_surf.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 48)))

    lines = [f"Tours : {game.turn_number}"]
    territories = {}
    for x in range(GRID_COLS):
        for y in range(GRID_ROWS):
            country = game.grid[x][y].country
            if country != Country.NONE:
                territories[country] = territories.get(country, 0) + 1
    ranked = sorted(territories.items(), key=lambda item: item[1], reverse=True)
    if ranked:
        bits = [f"{COUNTRY_NAMES[c]} {n}" for c, n in ranked[:5]]
        lines.append("Territoire : " + " · ".join(bits))
    looted = getattr(game, "gold_looted", {})
    if looted:
        best = max(looted.items(), key=lambda item: item[1])
        if best[1] > 0:
            lines.append(f"Or pillé : {COUNTRY_NAMES[best[0]]} +{best[1]}")

    y = panel_y + 110
    for line in lines:
        for wrapped in wrap_text(body, line, panel_w - 48):
            surf = body.render(wrapped, True, INK)
            screen.blit(surf, surf.get_rect(center=(WINDOW_WIDTH // 2, y)))
            y += 28
    hint = small.render("Clic ou Entrée : retour au menu", True, (90, 64, 36))
    screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, panel_y + panel_h - 40)))
