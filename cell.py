import pygame
from constants import *
from theme import GOLD, draw_hatch
from tiles import draw_army_badge, draw_city, terrain_surface


def draw_unit_icon(surface, cx, cy, unit_type, embarked=False):
    from tiles import _figure, _ship
    from constants import COUNTRY_COLORS, Country

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
            wash.fill((*COUNTRY_COLORS[self.country], 36))
            surface.blit(wash, (screen_x, screen_y))
            draw_hatch(
                surface,
                tile,
                COUNTRY_HATCH.get(self.country, "dots"),
                (*COUNTRY_COLORS[self.country], 70),
                step=6,
            )
            self._draw_political_borders(surface, screen_x, screen_y, grid)

        if self.terrain == TerrainType.WATER and grid is not None:
            self._draw_coast_foam(surface, screen_x, screen_y, grid)

        if self.is_capital or self.is_city:
            draw_city(surface, self, screen_x, screen_y, compact=bool(self.army and show_units))

        if show_units and self.army:
            draw_army_badge(surface, screen_x, screen_y, self.army, assets)

        pygame.draw.rect(surface, (58, 44, 28), tile, 1)
        if self.is_selected:
            pygame.draw.rect(surface, GOLD, tile.inflate(-2, -2), 2)

    def _neighbor(self, grid, dx, dy):
        nx, ny = self.x + dx, self.y + dy
        if grid is None or not (0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS):
            return None
        return grid[nx][ny]

    def _draw_political_borders(self, surface, screen_x, screen_y, grid):
        color = COUNTRY_COLORS[self.country]
        edges = (
            (0, -1, (screen_x, screen_y), (screen_x + CELL_SIZE - 1, screen_y)),
            (0, 1, (screen_x, screen_y + CELL_SIZE - 1), (screen_x + CELL_SIZE - 1, screen_y + CELL_SIZE - 1)),
            (-1, 0, (screen_x, screen_y), (screen_x, screen_y + CELL_SIZE - 1)),
            (1, 0, (screen_x + CELL_SIZE - 1, screen_y), (screen_x + CELL_SIZE - 1, screen_y + CELL_SIZE - 1)),
        )
        for dx, dy, start, end in edges:
            neighbor = self._neighbor(grid, dx, dy)
            other = Country.NONE if neighbor is None else neighbor.country
            if other != self.country:
                pygame.draw.line(surface, color, start, end, 3)

    def _draw_coast_foam(self, surface, screen_x, screen_y, grid):
        foam = (168, 196, 204)
        edges = (
            (0, -1, (screen_x + 2, screen_y + 2), (screen_x + CELL_SIZE - 3, screen_y + 2)),
            (0, 1, (screen_x + 2, screen_y + CELL_SIZE - 3), (screen_x + CELL_SIZE - 3, screen_y + CELL_SIZE - 3)),
            (-1, 0, (screen_x + 2, screen_y + 2), (screen_x + 2, screen_y + CELL_SIZE - 3)),
            (1, 0, (screen_x + CELL_SIZE - 3, screen_y + 2), (screen_x + CELL_SIZE - 3, screen_y + CELL_SIZE - 3)),
        )
        for dx, dy, start, end in edges:
            neighbor = self._neighbor(grid, dx, dy)
            if neighbor and neighbor.terrain in SHORE_TERRAINS:
                pygame.draw.line(surface, foam, start, end, 2)
