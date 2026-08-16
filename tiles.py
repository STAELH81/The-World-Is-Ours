"""Tuiles et figurines procédurales, style Civilization I (pixel art 36 px)."""

import pygame
from constants import *
from theme import CREAM, GOLD, INK, PARCHMENT, WOOD_DARK, load_font

_TERRAIN = {}
_UNITS = {}


def _clamp(color):
    return tuple(max(0, min(255, int(c))) for c in color)


def _dither(surf, a, b, variant):
    surf.fill(a)
    w, h = surf.get_size()
    for y in range(variant % 2, h, 2):
        for x in range((y + variant) % 2, w, 2):
            surf.set_at((x, y), b)


def _tuft(surf, x, y, color):
    pygame.draw.line(surf, color, (x, y + 3), (x - 3, y), 1)
    pygame.draw.line(surf, color, (x, y + 3), (x + 3, y), 1)
    pygame.draw.line(surf, color, (x, y + 3), (x, y - 1), 1)


def _tree(surf, x, y, r):
    pygame.draw.rect(surf, (86, 58, 32), (x - 1, y + r - 2, 3, 7))
    pygame.draw.circle(surf, (22, 62, 26), (x, y), r)
    pygame.draw.circle(surf, (48, 98, 42), (x - 1, y - 2), max(2, r - 3))


def _make_terrain(terrain, variant):
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE))
    if terrain == TerrainType.PLAIN:
        _dither(surf, (132, 156, 78), (156, 176, 92), variant)
        for ox, oy in ((7, 10), (22, 8), (14, 24), (28, 20)):
            _tuft(surf, ox, oy, (78, 118, 48))
    elif terrain == TerrainType.FOREST:
        _dither(surf, (38, 78, 36), (28, 58, 26), variant)
        _tree(surf, 11, 12, 7)
        _tree(surf, 24, 14, 6)
        _tree(surf, 17, 24, 7)
        _tree(surf, 28, 26, 5)
    elif terrain == TerrainType.MOUNTAIN:
        s = CELL_SIZE
        _dither(surf, (128, 108, 78), (148, 128, 96), variant)
        pygame.draw.polygon(surf, (96, 82, 62), [(2, s - 2), (s // 3, 8), (s - 10, s - 2)])
        pygame.draw.polygon(surf, (168, 148, 112), [(8, s - 2), (s * 2 // 3, 4), (s - 2, s - 2)])
        pygame.draw.polygon(
            surf,
            PARCHMENT,
            [(s * 2 // 3, 8), (s * 2 // 3 + 5, 18), (s * 2 // 3 - 6, 18)],
        )
    elif terrain == TerrainType.WATER:
        deep = (28, 68, 112) if variant % 2 == 0 else (24, 62, 104)
        foam = (92, 148, 176)
        _dither(surf, deep, _clamp(c + 14 for c in deep), variant)
        y1 = 10 + variant
        y2 = 22 - variant
        pygame.draw.line(surf, foam, (2, y1), (CELL_SIZE - 3, y1 + 3), 1)
        pygame.draw.line(surf, foam, (4, y2), (CELL_SIZE - 2, y2 - 2), 1)
    elif terrain == TerrainType.BEACH:
        _dither(surf, (214, 192, 140), (232, 214, 168), variant)
        pygame.draw.line(surf, (186, 198, 176), (0, 28), (CELL_SIZE, 24), 3)
        for px, py in ((6, 8), (18, 14), (10, 22), (26, 18), (22, 8)):
            pygame.draw.circle(surf, (186, 164, 112), (px, py), 1)
    elif terrain == TerrainType.BRIDGE:
        _dither(surf, (28, 68, 112), (36, 80, 124), variant)
        pygame.draw.rect(surf, (118, 86, 48), (4, 8, CELL_SIZE - 8, CELL_SIZE - 16))
        for i in range(4):
            y = 10 + i * 6
            pygame.draw.line(surf, (168, 132, 78), (5, y), (CELL_SIZE - 6, y), 3)
        pygame.draw.line(surf, WOOD_DARK, (7, 6), (7, CELL_SIZE - 6), 2)
        pygame.draw.line(surf, WOOD_DARK, (CELL_SIZE - 8, 6), (CELL_SIZE - 8, CELL_SIZE - 6), 2)
    else:
        surf.fill(TERRAIN_COLORS.get(terrain, (80, 80, 80)))
    return surf


def terrain_surface(terrain, variant=0):
    key = (terrain, variant % 4, CELL_SIZE)
    cached = _TERRAIN.get(key)
    if cached is None:
        cached = _make_terrain(terrain, variant % 4)
        _TERRAIN[key] = cached
    return cached


def _figure(surf, cx, cy, unit_type, color):
    skin = (236, 214, 176)
    if unit_type == UnitType.CATAPULT:
        pygame.draw.rect(surf, (92, 62, 32), (cx - 12, cy + 2, 24, 9))
        pygame.draw.rect(surf, INK, (cx - 12, cy + 2, 24, 9), 2)
        pygame.draw.rect(surf, color, (cx - 10, cy + 4, 8, 5))
        pygame.draw.line(surf, WOOD_DARK, (cx - 6, cy + 4), (cx + 11, cy - 12), 3)
        pygame.draw.circle(surf, (90, 90, 96), (cx + 12, cy - 13), 5)
        pygame.draw.circle(surf, INK, (cx + 12, cy - 13), 5, 2)
        return
    pygame.draw.circle(surf, skin, (cx, cy - 9), 6)
    pygame.draw.circle(surf, INK, (cx, cy - 9), 6, 2)
    pygame.draw.rect(surf, color, (cx - 6, cy - 4, 12, 13))
    pygame.draw.rect(surf, INK, (cx - 6, cy - 4, 12, 13), 2)
    if unit_type == UnitType.SWORDSMAN:
        pygame.draw.line(surf, (230, 230, 236), (cx + 8, cy - 14), (cx + 8, cy + 8), 3)
        pygame.draw.line(surf, GOLD, (cx + 4, cy - 2), (cx + 12, cy - 2), 3)
        pygame.draw.circle(surf, (168, 168, 176), (cx - 8, cy + 2), 6)
        pygame.draw.circle(surf, INK, (cx - 8, cy + 2), 6, 2)
        pygame.draw.circle(surf, color, (cx - 8, cy + 2), 4)
    elif unit_type == UnitType.CROSSBOWMAN:
        pygame.draw.arc(surf, CREAM, (cx - 2, cy - 12, 18, 16), 0.35, 2.7, 3)
        pygame.draw.line(surf, GOLD, (cx, cy + 1), (cx + 12, cy + 2), 3)
        pygame.draw.circle(surf, CREAM, (cx + 12, cy + 2), 3)
        pygame.draw.circle(surf, INK, (cx + 12, cy + 2), 3, 1)
    elif unit_type == UnitType.SPEARMAN:
        pygame.draw.line(surf, (186, 150, 88), (cx + 8, cy + 10), (cx + 8, cy - 16), 3)
        pygame.draw.polygon(surf, (210, 210, 218), [(cx + 8, cy - 18), (cx + 4, cy - 10), (cx + 12, cy - 10)])
        pygame.draw.circle(surf, (168, 168, 176), (cx - 8, cy + 3), 5)
        pygame.draw.circle(surf, INK, (cx - 8, cy + 3), 5, 2)
    else:
        pygame.draw.ellipse(surf, (92, 62, 36), (cx - 14, cy - 2, 26, 14))
        pygame.draw.ellipse(surf, INK, (cx - 14, cy - 2, 26, 14), 2)
        pygame.draw.circle(surf, (92, 62, 36), (cx + 10, cy - 3), 5)
        pygame.draw.rect(surf, color, (cx - 5, cy - 10, 10, 10))
        pygame.draw.rect(surf, INK, (cx - 5, cy - 10, 10, 10), 1)
        pygame.draw.circle(surf, skin, (cx, cy - 12), 4)
        pygame.draw.circle(surf, INK, (cx, cy - 12), 4, 1)
        pygame.draw.line(surf, INK, (cx - 8, cy + 11), (cx - 8, cy + 4), 3)
        pygame.draw.line(surf, INK, (cx + 6, cy + 11), (cx + 6, cy + 4), 3)


def _ship(surf, cx, cy):
    pygame.draw.polygon(
        surf,
        (92, 64, 36),
        [(cx - 14, cy + 2), (cx + 14, cy + 2), (cx + 10, cy + 11), (cx - 10, cy + 11)],
    )
    pygame.draw.polygon(
        surf,
        INK,
        [(cx - 14, cy + 2), (cx + 14, cy + 2), (cx + 10, cy + 11), (cx - 10, cy + 11)],
        2,
    )
    pygame.draw.line(surf, INK, (cx, cy + 2), (cx, cy - 12), 3)
    pygame.draw.polygon(surf, CREAM, [(cx, cy - 13), (cx + 12, cy - 3), (cx, cy + 2)])
    pygame.draw.polygon(surf, INK, [(cx, cy - 13), (cx + 12, cy - 3), (cx, cy + 2)], 1)


def _make_unit(unit_type, country, embarked):
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    color = COUNTRY_COLORS[country]
    cx, cy = CELL_SIZE // 2, CELL_SIZE // 2 + 1
    if embarked:
        _ship(surf, cx, cy)
    else:
        _figure(surf, cx, cy, unit_type, color)
    return surf


def unit_surface(army):
    key = (army.unit_type, army.country, bool(army.embarked), CELL_SIZE)
    cached = _UNITS.get(key)
    if cached is None:
        cached = _make_unit(army.unit_type, army.country, army.embarked)
        _UNITS[key] = cached
    return cached


def _draw_unit_base(surface, screen_x, screen_y, color):
    cx = screen_x + CELL_SIZE // 2
    by = screen_y + CELL_SIZE - 12
    pygame.draw.ellipse(surface, (16, 10, 6), (cx - 16, by + 2, 32, 11))
    pygame.draw.ellipse(surface, color, (cx - 15, by, 30, 11))
    pygame.draw.ellipse(surface, INK, (cx - 15, by, 30, 11), 2)


def draw_army_badge(surface, screen_x, screen_y, army, assets=None):
    color = COUNTRY_COLORS[army.country]
    _draw_unit_base(surface, screen_x, screen_y, color)
    sprite = assets.units.get(army.unit_type) if assets else None
    cx = screen_x + CELL_SIZE // 2
    cy = screen_y + CELL_SIZE // 2 - 1
    if sprite and not army.embarked:
        surface.blit(sprite, sprite.get_rect(center=(cx, cy)))
    else:
        surface.blit(unit_surface(army), (screen_x, screen_y))
    count = str(army.count)
    count_font = load_font(14, bold=True)
    tw, th = count_font.size(count)
    badge = pygame.Rect(screen_x + CELL_SIZE - tw - 8, screen_y + CELL_SIZE - th - 5, tw + 6, th + 3)
    pygame.draw.rect(surface, color, badge, border_radius=3)
    pygame.draw.rect(surface, INK, badge, 1, border_radius=3)
    surface.blit(count_font.render(count, True, CREAM), (badge.x + 3, badge.y + 1))


def draw_city(surface, cell, screen_x, screen_y, compact=False, assets=None):
    key = "capital" if cell.is_capital else "city"
    sprite = assets.buildings.get(key) if assets else None
    if sprite:
        cy = screen_y + CELL_SIZE // 2 - (4 if compact else 0)
        surface.blit(sprite, sprite.get_rect(center=(screen_x + CELL_SIZE // 2, cy)))
        return
    color = COUNTRY_COLORS.get(cell.country, (120, 90, 50))
    cx = screen_x + CELL_SIZE // 2
    base_y = screen_y + CELL_SIZE - (10 if compact else 7)
    width = 18 if compact else 24
    height = 10 if compact else 14
    wall = pygame.Rect(cx - width // 2, base_y - height, width, height)
    pygame.draw.rect(surface, (72, 56, 38), wall)
    pygame.draw.rect(surface, color, wall, 1)
    for i in range(0, width - 2, 4):
        pygame.draw.rect(surface, (92, 72, 48), (wall.x + 1 + i, wall.y - 3, 3, 4))
    if cell.is_capital:
        pygame.draw.rect(surface, WOOD_DARK, (cx - 5, base_y - height - 8, 10, 10))
        pygame.draw.polygon(
            surface,
            GOLD,
            [(cx - 7, base_y - height - 8), (cx, base_y - height - 16), (cx + 7, base_y - height - 8)],
        )
        pygame.draw.line(surface, color, (cx + 6, base_y - height - 16), (cx + 6, base_y - height - 6), 2)
    else:
        pygame.draw.rect(surface, (110, 86, 54), (cx - 4, base_y - height - 6, 8, 8))
        pygame.draw.rect(surface, INK, (cx - 1, base_y - 6, 2, 5))
