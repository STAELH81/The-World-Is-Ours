import pygame
from constants import *
from theme import GOLD
from tiles import draw_army_badge, draw_city, terrain_surface


def draw_unit_icon(surface, cx, cy, unit_type, embarked=False):
    from tiles import _figure, _ship

    if embarked:
        _ship(surface, cx, cy)
        return
    _figure(surface, cx, cy, unit_type, COUNTRY_COLORS[Country.RED])


def draw_army_at(surface, screen_x, screen_y, army, assets=None):
    draw_army_badge(surface, screen_x, screen_y, army, assets)


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
        self.garrison_ready = True

    def draw(self, surface, assets=None, show_units=True, tick=0, grid=None):
        screen_x, screen_y = cell_screen_pos(self.x, self.y)
        variant = (self.x * 3 + self.y * 5) % 4
        if self.terrain == TerrainType.WATER:
            variant = (variant + (tick // 480)) % 4
        surface.blit(terrain_surface(self.terrain, variant), (screen_x, screen_y))

        if assets:
            sprite = assets.terrain.get(self.terrain)
            if sprite:
                surface.blit(sprite, (screen_x, screen_y))

        tile = pygame.Rect(screen_x, screen_y, CELL_SIZE, CELL_SIZE)
        if self.country != Country.NONE:
            wash = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            wash.fill((*COUNTRY_COLORS[self.country], 28))
            surface.blit(wash, (screen_x, screen_y))
            self._draw_political_borders(surface, screen_x, screen_y, grid)

        if self.terrain == TerrainType.WATER and grid is not None:
            self._draw_coast_foam(surface, screen_x, screen_y, grid)

        if self.is_capital or self.is_city:
            draw_city(
                surface,
                self,
                screen_x,
                screen_y,
                compact=bool(self.army and show_units),
                assets=assets,
            )

        if show_units and self.army:
            draw_army_badge(surface, screen_x, screen_y, self.army, assets)

        if self.is_selected:
            pygame.draw.rect(surface, GOLD, tile.inflate(-2, -2), 2)

    def _neighbor(self, grid, dx, dy):
        nx, ny = self.x + dx, self.y + dy
        if grid is None or not (0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS):
            return None
        return grid[nx][ny]

    def territory_edge_kind(self, neighbor):
        """same = interior, outer = blob outline, frontier = other kingdom."""
        if neighbor is None:
            return "outer"
        if neighbor.country == self.country:
            return "same"
        if neighbor.country != Country.NONE:
            return "frontier"
        return "outer"

    def political_edges(self, grid):
        return {
            "n": self.territory_edge_kind(self._neighbor(grid, 0, -1)),
            "s": self.territory_edge_kind(self._neighbor(grid, 0, 1)),
            "w": self.territory_edge_kind(self._neighbor(grid, -1, 0)),
            "e": self.territory_edge_kind(self._neighbor(grid, 1, 0)),
        }

    def _edge_rect(self, name, thickness, inset=0):
        s = CELL_SIZE
        if name == "n":
            return pygame.Rect(inset, inset, s - 2 * inset, thickness)
        if name == "s":
            return pygame.Rect(inset, s - thickness - inset, s - 2 * inset, thickness)
        if name == "w":
            return pygame.Rect(inset, inset, thickness, s - 2 * inset)
        return pygame.Rect(s - thickness - inset, inset, thickness, s - 2 * inset)

    def _draw_political_borders(self, surface, screen_x, screen_y, grid):
        """Strong outline between kingdoms; faint grid between tiles inside a kingdom."""
        color = COUNTRY_COLORS[self.country]
        layer = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        kinds = self.political_edges(grid)

        for name, kind in kinds.items():
            if kind == "same":
                # One side only so the shared edge stays a single hairline.
                if name in ("e", "s"):
                    pygame.draw.rect(layer, (28, 20, 12, 48), self._edge_rect(name, 1))
                continue
            pygame.draw.rect(layer, (*color, 70), self._edge_rect(name, 6))
            pygame.draw.rect(layer, (18, 12, 8, 200), self._edge_rect(name, 2))
            pygame.draw.rect(layer, (*color, 230), self._edge_rect(name, 2, inset=1))

        surface.blit(layer, (screen_x, screen_y))

    def _draw_coast_foam(self, surface, screen_x, screen_y, grid):
        foam = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        edges = (
            (0, -1, "n"),
            (0, 1, "s"),
            (-1, 0, "w"),
            (1, 0, "e"),
        )
        for dx, dy, name in edges:
            neighbor = self._neighbor(grid, dx, dy)
            if neighbor and neighbor.terrain in SHORE_TERRAINS:
                pygame.draw.rect(foam, (200, 220, 224, 90), self._edge_rect(name, 2, inset=1))
        surface.blit(foam, (screen_x, screen_y))
