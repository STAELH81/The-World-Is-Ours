"""Tuiles et figurines procédurales, style Civilization I (pixel art 36 px)."""

import pygame
from constants import *
from theme import CREAM, GOLD, INK, PARCHMENT, WOOD_DARK, blit_outlined, load_font

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
        _dither(surf, (128, 108, 78), (148, 128, 96), variant)
        pygame.draw.polygon(surf, (96, 82, 62), [(2, 34), (14, 8), (26, 34)])
        pygame.draw.polygon(surf, (168, 148, 112), [(10, 34), (22, 4), (34, 34)])
        pygame.draw.polygon(surf, PARCHMENT, [(22, 8), (26, 16), (18, 16)])
        pygame.draw.polygon(surf, (220, 214, 196), [(14, 12), (16, 18), (11, 18)])
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
    pygame.draw.circle(surf, skin, (cx, cy - 7), 4)
    pygame.draw.circle(surf, INK, (cx, cy - 7), 4, 1)
    pygame.draw.rect(surf, color, (cx - 4, cy - 3, 8, 9))
    pygame.draw.rect(surf, INK, (cx - 4, cy - 3, 8, 9), 1)
    if unit_type == UnitType.SWORDSMAN:
        pygame.draw.line(surf, (210, 210, 218), (cx + 6, cy - 10), (cx + 6, cy + 6), 2)
        pygame.draw.line(surf, GOLD, (cx + 3, cy - 2), (cx + 9, cy - 2), 2)
        pygame.draw.circle(surf, (160, 160, 168), (cx - 6, cy + 1), 4)
        pygame.draw.circle(surf, color, (cx - 6, cy + 1), 4, 1)
    elif unit_type == UnitType.CROSSBOWMAN:
        pygame.draw.arc(surf, CREAM, (cx - 2, cy - 8, 16, 14), 0.4, 2.6, 2)
        pygame.draw.line(surf, GOLD, (cx, cy), (cx + 10, cy + 1), 2)
        pygame.draw.circle(surf, CREAM, (cx + 10, cy + 1), 2)
    else:
        pygame.draw.ellipse(surf, (92, 62, 36), (cx - 11, cy - 1, 20, 11))
        pygame.draw.circle(surf, (92, 62, 36), (cx + 8, cy - 2), 4)
        pygame.draw.rect(surf, color, (cx - 3, cy - 8, 7, 8))
        pygame.draw.circle(surf, skin, (cx, cy - 10), 3)
        pygame.draw.line(surf, INK, (cx - 6, cy + 9), (cx - 6, cy + 3), 2)
        pygame.draw.line(surf, INK, (cx + 5, cy + 9), (cx + 5, cy + 3), 2)


def _ship(surf, cx, cy):
    pygame.draw.polygon(
        surf,
        (92, 64, 36),
        [(cx - 12, cy + 2), (cx + 12, cy + 2), (cx + 8, cy + 9), (cx - 8, cy + 9)],
    )
    pygame.draw.line(surf, INK, (cx, cy + 2), (cx, cy - 10), 2)
    pygame.draw.polygon(surf, CREAM, [(cx, cy - 11), (cx + 10, cy - 3), (cx, cy + 1)])
    pygame.draw.polygon(surf, INK, [(cx, cy - 11), (cx + 10, cy - 3), (cx, cy + 1)], 1)


def _make_unit(unit_type, country, embarked):
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    color = COUNTRY_COLORS[country]
    box = pygame.Rect(5, 6, CELL_SIZE - 10, CELL_SIZE - 11)
    pygame.draw.rect(surf, (36, 24, 14), box)
    inner = box.inflate(-3, -3)
    pygame.draw.rect(surf, color, inner)
    pygame.draw.rect(surf, GOLD, inner, 1)
    cx, cy = inner.centerx, inner.centery + 2
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


def draw_army_badge(surface, screen_x, screen_y, army, assets=None):
    sprite = assets.units.get(army.unit_type) if assets else None
    if sprite and not army.embarked:
        box = pygame.Rect(screen_x + 5, screen_y + 6, CELL_SIZE - 10, CELL_SIZE - 11)
        pygame.draw.rect(surface, COUNTRY_COLORS[army.country], box)
        pygame.draw.rect(surface, GOLD, box, 1)
        surface.blit(sprite, sprite.get_rect(center=box.center))
    else:
        surface.blit(unit_surface(army), (screen_x, screen_y))
    letter = UNIT_LETTERS.get(army.unit_type, "?")
    font = load_font(14, bold=True)
    blit_outlined(surface, font, letter, CREAM, INK, (screen_x + 7, screen_y + 5))
    count = f"~{army.count}" if army.embarked else str(army.count)
    count_font = load_font(13, bold=True)
    label = count_font.render(count, True, CREAM)
    shadow = count_font.render(count, True, INK)
    pos = (screen_x + CELL_SIZE - 4 - label.get_width(), screen_y + CELL_SIZE - 16)
    surface.blit(shadow, (pos[0] + 1, pos[1] + 1))
    surface.blit(label, pos)


def draw_city(surface, cell, screen_x, screen_y, compact=False):
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
