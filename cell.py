import math
import pygame
from constants import *


def _clamp_color(color):
    return tuple(max(0, min(255, int(c))) for c in color)


def _tile_vary(x, y):
    return ((x * 73 + y * 137) % 13) - 6


def draw_unit_icon(surface, cx, cy, unit_type, embarked=False):
    white = (245, 245, 245)
    dark = (20, 22, 28)
    if embarked:
        pygame.draw.polygon(
            surface,
            (90, 64, 40),
            [(cx - 9, cy + 2), (cx + 9, cy + 2), (cx + 6, cy + 8), (cx - 6, cy + 8)],
        )
        pygame.draw.line(surface, dark, (cx, cy + 2), (cx, cy - 8), 2)
        pygame.draw.polygon(surface, white, [(cx, cy - 8), (cx + 7, cy - 3), (cx, cy - 1)])
        return
    if unit_type == UnitType.SWORDSMAN:
        pygame.draw.polygon(surface, (180, 180, 190), [(cx, cy - 8), (cx + 3, cy + 6), (cx - 3, cy + 6)])
        pygame.draw.line(surface, white, (cx, cy - 9), (cx, cy + 7), 2)
        pygame.draw.line(surface, (200, 170, 80), (cx - 4, cy - 1), (cx + 4, cy - 1), 2)
    elif unit_type == UnitType.CROSSBOWMAN:
        pygame.draw.arc(surface, white, (cx - 8, cy - 7, 16, 14), 0.4, 2.7, 2)
        pygame.draw.line(surface, (200, 170, 80), (cx - 2, cy), (cx + 8, cy), 2)
        pygame.draw.circle(surface, white, (cx + 8, cy), 2)
    else:
        pygame.draw.ellipse(surface, (90, 60, 40), (cx - 8, cy - 2, 16, 10))
        pygame.draw.circle(surface, (90, 60, 40), (cx + 6, cy - 3), 4)
        pygame.draw.line(surface, dark, (cx - 4, cy + 7), (cx - 4, cy + 2), 2)
        pygame.draw.line(surface, dark, (cx + 4, cy + 7), (cx + 4, cy + 2), 2)


def draw_army_at(surface, screen_x, screen_y, army, assets=None):
    army_bg = pygame.Surface((CELL_SIZE - 6, CELL_SIZE - 6), pygame.SRCALPHA)
    army_bg.fill((*COUNTRY_COLORS[army.country], 185))
    surface.blit(army_bg, (screen_x + 3, screen_y + 3))
    pygame.draw.rect(
        surface,
        COUNTRY_COLORS[army.country],
        (screen_x + 3, screen_y + 3, CELL_SIZE - 6, CELL_SIZE - 6),
        1,
    )
    unit_sprite = assets.units.get(army.unit_type) if assets else None
    if unit_sprite and not army.embarked:
        sprite_rect = unit_sprite.get_rect(center=(screen_x + CELL_SIZE // 2, screen_y + 13))
        surface.blit(unit_sprite, sprite_rect)
    else:
        draw_unit_icon(
            surface,
            screen_x + CELL_SIZE // 2,
            screen_y + 13,
            army.unit_type,
            embarked=army.embarked,
        )
    font_count = pygame.font.Font(None, 18)
    label = f"~{army.count}" if army.embarked else f"x{army.count}"
    count_text = font_count.render(label, True, (255, 255, 255))
    count_rect = count_text.get_rect(center=(screen_x + CELL_SIZE // 2, screen_y + CELL_SIZE - 8))
    surface.blit(count_text, count_rect)


class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.terrain = TerrainType.WATER
        self.country = Country.NONE
        self.is_selected = False
        self.is_capital = False
        self.is_city = False
        self.army = None
        self.bridge_hp = 0
        self.discovered_by = set()
        self.capital_owner = Country.NONE
        self.city_owner = Country.NONE
        self.last_recruit_turn = -1

    def draw(self, surface, assets=None, show_units=True, tick=0):
        screen_x = self.x * CELL_SIZE
        screen_y = self.y * CELL_SIZE
        vary = _tile_vary(self.x, self.y)
        color = _clamp_color(c + vary for c in TERRAIN_COLORS[self.terrain])
        if self.is_selected:
            color = _clamp_color(c + 50 for c in color)

        terrain_sprite = assets.terrain.get(self.terrain) if assets else None
        if terrain_sprite:
            surface.blit(terrain_sprite, (screen_x, screen_y))
            if self.is_selected:
                overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                overlay.fill((255, 255, 255, 45))
                surface.blit(overlay, (screen_x, screen_y))
        else:
            self._draw_procedural_terrain(surface, screen_x, screen_y, color, tick)

        if self.country != Country.NONE:
            border_overlay = assets.overlays.get(self.country) if assets else None
            if border_overlay:
                surface.blit(border_overlay, (screen_x, screen_y))
            else:
                pygame.draw.rect(
                    surface,
                    COUNTRY_COLORS[self.country],
                    (screen_x, screen_y, CELL_SIZE, CELL_SIZE),
                    3,
                )

        if self.is_capital:
            center_x = screen_x + CELL_SIZE // 2
            center_y = screen_y + CELL_SIZE // 2
            capital_sprite = assets.buildings.get("capital") if assets else None
            if capital_sprite:
                surface.blit(capital_sprite, capital_sprite.get_rect(center=(center_x, center_y)))
            else:
                pygame.draw.circle(surface, COUNTRY_COLORS[self.country], (center_x, center_y), 10)
                pygame.draw.polygon(
                    surface,
                    (255, 220, 120),
                    [(center_x, center_y - 7), (center_x + 5, center_y + 4), (center_x - 5, center_y + 4)],
                )
        elif self.is_city:
            center_x = screen_x + CELL_SIZE // 2
            center_y = screen_y + CELL_SIZE // 2
            city_sprite = assets.buildings.get("city") if assets else None
            if city_sprite:
                surface.blit(city_sprite, city_sprite.get_rect(center=(center_x, center_y)))
            else:
                pygame.draw.rect(surface, COUNTRY_COLORS[self.country], (center_x - 8, center_y - 8, 16, 16))
                pygame.draw.rect(surface, (20, 20, 24), (center_x - 4, center_y - 1, 3, 9))
                pygame.draw.rect(surface, (255, 230, 140), (center_x + 2, center_y - 5, 4, 4))

        if show_units and self.army:
            draw_army_at(surface, screen_x, screen_y, self.army, assets)

    def _draw_procedural_terrain(self, surface, screen_x, screen_y, color, tick):
        pygame.draw.rect(surface, color, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))
        shade = _clamp_color(c - 26 for c in color)
        pygame.draw.rect(surface, shade, (screen_x, screen_y + CELL_SIZE // 2, CELL_SIZE, CELL_SIZE // 2))

        if self.terrain == TerrainType.WATER:
            wave = math.sin(tick / 420 + self.x * 0.45 + self.y * 0.22)
            y_off = int(2 * wave)
            foam = _clamp_color(c + 28 for c in TERRAIN_COLORS[TerrainType.WATER])
            pygame.draw.line(surface, foam, (screen_x + 2, screen_y + 10 + y_off), (screen_x + CELL_SIZE - 3, screen_y + 14 + y_off), 1)
            pygame.draw.line(surface, foam, (screen_x + 4, screen_y + 22 - y_off), (screen_x + CELL_SIZE - 2, screen_y + 18 - y_off), 1)
        elif self.terrain == TerrainType.BEACH:
            pygame.draw.circle(surface, (235, 220, 180), (screen_x + 8, screen_y + 10), 2)
            pygame.draw.circle(surface, (180, 200, 210), (screen_x + 22, screen_y + 24), 2)
        elif self.terrain == TerrainType.FOREST:
            pygame.draw.circle(surface, (28, 70, 22), (screen_x + 12, screen_y + 14), 7)
            pygame.draw.circle(surface, (36, 88, 28), (screen_x + 22, screen_y + 18), 6)
            pygame.draw.circle(surface, (24, 58, 18), (screen_x + 16, screen_y + 24), 5)
        elif self.terrain == TerrainType.MOUNTAIN:
            pygame.draw.polygon(
                surface,
                (150, 120, 90),
                [(screen_x + 6, screen_y + CELL_SIZE - 4), (screen_x + CELL_SIZE // 2, screen_y + 4), (screen_x + CELL_SIZE - 5, screen_y + CELL_SIZE - 4)],
            )
            pygame.draw.polygon(
                surface,
                (230, 230, 235),
                [(screen_x + CELL_SIZE // 2, screen_y + 6), (screen_x + CELL_SIZE // 2 + 5, screen_y + 16), (screen_x + CELL_SIZE // 2 - 5, screen_y + 16)],
            )
        elif self.terrain == TerrainType.BRIDGE:
            plank = (160, 130, 80)
            for i in range(3):
                y = screen_y + 8 + i * 8
                pygame.draw.line(surface, plank, (screen_x + 4, y), (screen_x + CELL_SIZE - 4, y), 3)
            pygame.draw.line(surface, (70, 50, 30), (screen_x + 6, screen_y + 4), (screen_x + 6, screen_y + CELL_SIZE - 4), 2)
            pygame.draw.line(surface, (70, 50, 30), (screen_x + CELL_SIZE - 7, screen_y + 4), (screen_x + CELL_SIZE - 7, screen_y + CELL_SIZE - 4), 2)
        else:
            pygame.draw.circle(surface, _clamp_color(c + 18 for c in color), (screen_x + 10, screen_y + 8), 2)
        pygame.draw.rect(surface, (18, 18, 22), (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 1)
