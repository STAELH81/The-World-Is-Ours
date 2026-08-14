import math
import pygame
from constants import *
from theme import CREAM, GOLD, INK, PARCHMENT, WOOD_DARK, draw_hatch, load_font


def _clamp_color(color):
    return tuple(max(0, min(255, int(c))) for c in color)


def _tile_vary(x, y):
    return ((x * 73 + y * 137) % 11) - 5


def draw_unit_icon(surface, cx, cy, unit_type, embarked=False):
    if embarked:
        pygame.draw.polygon(
            surface,
            (92, 64, 36),
            [(cx - 10, cy + 3), (cx + 10, cy + 3), (cx + 7, cy + 9), (cx - 7, cy + 9)],
        )
        pygame.draw.line(surface, INK, (cx, cy + 3), (cx, cy - 8), 2)
        pygame.draw.polygon(surface, CREAM, [(cx, cy - 9), (cx + 8, cy - 3), (cx, cy)])
        return
    if unit_type == UnitType.SWORDSMAN:
        pygame.draw.polygon(surface, (188, 188, 196), [(cx, cy - 9), (cx + 4, cy + 7), (cx - 4, cy + 7)])
        pygame.draw.line(surface, CREAM, (cx, cy - 10), (cx, cy + 8), 2)
        pygame.draw.line(surface, GOLD, (cx - 5, cy - 1), (cx + 5, cy - 1), 2)
    elif unit_type == UnitType.CROSSBOWMAN:
        pygame.draw.arc(surface, CREAM, (cx - 9, cy - 8, 18, 16), 0.35, 2.8, 2)
        pygame.draw.line(surface, GOLD, (cx - 2, cy), (cx + 9, cy), 2)
        pygame.draw.circle(surface, CREAM, (cx + 9, cy), 2)
    else:
        pygame.draw.ellipse(surface, (92, 62, 38), (cx - 9, cy - 2, 18, 11))
        pygame.draw.circle(surface, (92, 62, 38), (cx + 7, cy - 3), 4)
        pygame.draw.line(surface, INK, (cx - 5, cy + 8), (cx - 5, cy + 2), 2)
        pygame.draw.line(surface, INK, (cx + 5, cy + 8), (cx + 5, cy + 2), 2)


def draw_army_at(surface, screen_x, screen_y, army, assets=None):
    box = pygame.Rect(screen_x + 3, screen_y + 3, CELL_SIZE - 6, CELL_SIZE - 6)
    pygame.draw.rect(surface, (42, 28, 16), box)
    pygame.draw.rect(surface, COUNTRY_COLORS[army.country], box, 2)
    unit_sprite = assets.units.get(army.unit_type) if assets else None
    if unit_sprite and not army.embarked:
        sprite_rect = unit_sprite.get_rect(center=box.center)
        surface.blit(unit_sprite, sprite_rect)
    letter = UNIT_LETTERS.get(army.unit_type, "?")
    font = load_font(20, bold=True)
    glyph = font.render(letter, True, CREAM)
    surface.blit(glyph, glyph.get_rect(center=(box.centerx, box.centery - 4)))
    if army.embarked:
        pygame.draw.polygon(
            surface,
            (120, 86, 48),
            [
                (box.centerx - 8, box.centery + 4),
                (box.centerx + 8, box.centery + 4),
                (box.centerx + 5, box.bottom - 3),
                (box.centerx - 5, box.bottom - 3),
            ],
        )
    count_font = load_font(15, bold=True)
    label = f"~{army.count}" if army.embarked else str(army.count)
    count = count_font.render(label, True, CREAM)
    surface.blit(count, count.get_rect(bottomright=(box.right - 1, box.bottom - 1)))


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
        screen_x, screen_y = cell_screen_pos(self.x, self.y)
        vary = _tile_vary(self.x, self.y)
        color = _clamp_color(c + vary for c in TERRAIN_COLORS[self.terrain])
        if self.is_selected:
            color = _clamp_color(c + 36 for c in color)

        terrain_sprite = assets.terrain.get(self.terrain) if assets else None
        if terrain_sprite:
            surface.blit(terrain_sprite, (screen_x, screen_y))
        else:
            self._draw_procedural_terrain(surface, screen_x, screen_y, color, tick)

        tile = pygame.Rect(screen_x, screen_y, CELL_SIZE, CELL_SIZE)
        if self.country != Country.NONE:
            wash = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            wash.fill((*COUNTRY_COLORS[self.country], 48))
            surface.blit(wash, (screen_x, screen_y))
            draw_hatch(
                surface,
                tile,
                COUNTRY_HATCH.get(self.country, "dots"),
                (*COUNTRY_COLORS[self.country], 110),
                step=5,
            )
            pygame.draw.rect(surface, COUNTRY_COLORS[self.country], tile, 2)

        if self.is_capital or self.is_city:
            self._draw_city(surface, screen_x, screen_y)

        if show_units and self.army:
            draw_army_at(surface, screen_x, screen_y, self.army, assets)

        pygame.draw.rect(surface, (78, 58, 32), tile, 1)
        if self.is_selected:
            pygame.draw.rect(surface, GOLD, tile.inflate(-2, -2), 2)

    def _draw_city(self, surface, screen_x, screen_y):
        cx = screen_x + CELL_SIZE // 2
        cy = screen_y + CELL_SIZE // 2
        color = COUNTRY_COLORS.get(self.country, (120, 90, 50))
        if self.is_capital:
            pygame.draw.rect(surface, WOOD_DARK, (cx - 10, cy - 6, 20, 14))
            pygame.draw.polygon(surface, GOLD, [(cx - 11, cy - 6), (cx, cy - 14), (cx + 11, cy - 6)])
            pygame.draw.rect(surface, color, (cx - 10, cy - 6, 20, 14), 1)
        else:
            pygame.draw.rect(surface, (92, 72, 48), (cx - 8, cy - 7, 16, 14))
            pygame.draw.rect(surface, color, (cx - 8, cy - 7, 16, 14), 1)
            pygame.draw.rect(surface, INK, (cx - 3, cy, 3, 7))

    def _draw_procedural_terrain(self, surface, screen_x, screen_y, color, tick):
        pygame.draw.rect(surface, color, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))
        if self.terrain == TerrainType.WATER:
            wave = math.sin(tick / 480 + self.x * 0.4 + self.y * 0.2)
            y_off = int(2 * wave)
            foam = _clamp_color(c + 36 for c in TERRAIN_COLORS[TerrainType.WATER])
            pygame.draw.line(surface, foam, (screen_x + 2, screen_y + 11 + y_off), (screen_x + CELL_SIZE - 3, screen_y + 15 + y_off), 1)
            pygame.draw.line(surface, foam, (screen_x + 4, screen_y + 24 - y_off), (screen_x + CELL_SIZE - 2, screen_y + 20 - y_off), 1)
        elif self.terrain == TerrainType.BEACH:
            for i, (px, py) in enumerate(((6, 8), (18, 14), (10, 24), (26, 22), (22, 8))):
                pygame.draw.circle(surface, (232, 216, 168) if i % 2 == 0 else (186, 198, 176), (screen_x + px, screen_y + py), 2)
        elif self.terrain == TerrainType.FOREST:
            for ox, oy, r in ((10, 12, 7), (22, 16, 6), (16, 24, 6), (26, 24, 5)):
                pygame.draw.circle(surface, (28, 70, 28), (screen_x + ox, screen_y + oy), r)
                pygame.draw.circle(surface, (52, 102, 44), (screen_x + ox - 1, screen_y + oy - 2), max(2, r - 3))
        elif self.terrain == TerrainType.MOUNTAIN:
            pygame.draw.polygon(
                surface,
                (168, 140, 104),
                [(screen_x + 4, screen_y + CELL_SIZE - 4), (screen_x + CELL_SIZE // 2, screen_y + 3), (screen_x + CELL_SIZE - 4, screen_y + CELL_SIZE - 4)],
            )
            pygame.draw.polygon(
                surface,
                PARCHMENT,
                [(screen_x + CELL_SIZE // 2, screen_y + 6), (screen_x + CELL_SIZE // 2 + 5, screen_y + 16), (screen_x + CELL_SIZE // 2 - 5, screen_y + 16)],
            )
        elif self.terrain == TerrainType.BRIDGE:
            plank = (168, 132, 78)
            for i in range(3):
                y = screen_y + 8 + i * 8
                pygame.draw.line(surface, plank, (screen_x + 4, y), (screen_x + CELL_SIZE - 4, y), 3)
            pygame.draw.line(surface, (70, 48, 28), (screen_x + 6, screen_y + 4), (screen_x + 6, screen_y + CELL_SIZE - 4), 2)
            pygame.draw.line(surface, (70, 48, 28), (screen_x + CELL_SIZE - 7, screen_y + 4), (screen_x + CELL_SIZE - 7, screen_y + CELL_SIZE - 4), 2)
        else:
            for ox, oy in ((8, 7), (20, 11), (14, 22), (28, 20)):
                pygame.draw.circle(surface, _clamp_color(c + 22 for c in color), (screen_x + ox, screen_y + oy), 1)
