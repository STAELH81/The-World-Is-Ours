"""Charte visuelle type Civilization I : bois, or, parchemin, texte lisible."""

import pygame

WOOD = (86, 54, 28)
WOOD_LIGHT = (122, 82, 44)
WOOD_DARK = (48, 28, 14)
GOLD = (212, 168, 78)
GOLD_BRIGHT = (240, 208, 120)
PARCHMENT = (236, 220, 184)
INK = (36, 24, 14)
INK_SOFT = (70, 52, 32)
CREAM = (255, 244, 214)

_FONT_CACHE = {}
_FONT_NAMES = (
    "Palatino Linotype",
    "Georgia",
    "Times New Roman",
    "DejaVu Serif",
    "Liberation Serif",
    "FreeSerif",
    "serif",
)


def load_font(size, bold=False):
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    font = pygame.font.SysFont(list(_FONT_NAMES), size, bold=bold)
    _FONT_CACHE[key] = font
    return font


def draw_bevel_rect(surface, rect, fill, light, dark, border=2):
    pygame.draw.rect(surface, fill, rect)
    pygame.draw.line(surface, light, rect.topleft, (rect.right - 1, rect.top), border)
    pygame.draw.line(surface, light, rect.topleft, (rect.left, rect.bottom - 1), border)
    pygame.draw.line(surface, dark, (rect.left, rect.bottom - 1), (rect.right - 1, rect.bottom - 1), border)
    pygame.draw.line(surface, dark, (rect.right - 1, rect.top), (rect.right - 1, rect.bottom - 1), border)


def draw_panel(surface, rect, title=None):
    draw_bevel_rect(surface, rect, WOOD, GOLD_BRIGHT, WOOD_DARK, 2)
    inner = rect.inflate(-6, -6)
    pygame.draw.rect(surface, (118, 86, 52), inner)
    pygame.draw.rect(surface, GOLD, inner, 1)
    parchment = inner.inflate(-6, -6)
    pygame.draw.rect(surface, PARCHMENT, parchment)
    if title:
        font = load_font(22, bold=True)
        surf = font.render(title, True, GOLD_BRIGHT)
        surface.blit(surf, (rect.x + 14, rect.y + 6))
    return parchment


def wrap_text(font, text, max_width):
    words = text.split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if font.size(trial)[0] <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_hatch(surface, rect, kind, color, step=4):
    overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    shade = (*color[:3], color[3] if len(color) > 3 else 90)
    if kind == "diag":
        for i in range(-rect.height, rect.width, step):
            pygame.draw.line(overlay, shade, (i, 0), (i + rect.height, rect.height), 1)
    elif kind == "diag2":
        for i in range(0, rect.width + rect.height, step):
            pygame.draw.line(overlay, shade, (i, 0), (i - rect.height, rect.height), 1)
    elif kind == "horiz":
        for y in range(1, rect.height, step):
            pygame.draw.line(overlay, shade, (0, y), (rect.width, y), 1)
    elif kind == "vert":
        for x in range(1, rect.width, step):
            pygame.draw.line(overlay, shade, (x, 0), (x, rect.height), 1)
    elif kind == "dots":
        for y in range(2, rect.height, step + 1):
            for x in range(2 + (y // 2) % 2 * 2, rect.width, step + 1):
                overlay.set_at((x, y), shade)
    surface.blit(overlay, rect.topleft)
