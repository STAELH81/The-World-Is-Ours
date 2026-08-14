"""Les tuiles Civ se dessinent sans planter."""

import unittest

import pygame

from army import Army
from cell import Cell
from constants import CELL_SIZE, Country, GRID_COLS, GRID_ROWS, HUD_TOP, TerrainType, UnitType, cell_screen_pos


class TileRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    def test_terrain_and_units_blit_to_a_surface(self):
        grid = [[Cell(x, y) for y in range(GRID_ROWS)] for x in range(GRID_COLS)]
        for x in range(6):
            for y in range(6):
                cell = grid[x][y]
                cell.terrain = [
                    TerrainType.PLAIN,
                    TerrainType.FOREST,
                    TerrainType.MOUNTAIN,
                    TerrainType.WATER,
                    TerrainType.BEACH,
                    TerrainType.BRIDGE,
                ][y]
                cell.country = Country.RED if x < 3 else Country.BLUE
        grid[1][1].army = Army(Country.RED, UnitType.SWORDSMAN, 3)
        grid[1][1].is_capital = True
        grid[4][0].army = Army(Country.BLUE, UnitType.CAVALRY, 2)
        grid[2][3].army = Army(Country.RED, UnitType.CROSSBOWMAN, 1)
        grid[2][3].army.embarked = True
        surf = pygame.Surface((CELL_SIZE * 6, HUD_TOP + CELL_SIZE * 6))
        for x in range(6):
            for y in range(6):
                grid[x][y].draw(surf, grid=grid)
        px, py = cell_screen_pos(1, 0)
        self.assertNotEqual(surf.get_at((px + 4, py + 4))[:3], (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
