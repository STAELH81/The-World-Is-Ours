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

    def test_embarked_army_can_use_a_ship_sprite(self):
        from tiles import draw_army_badge

        class Assets:
            units = {}
            ship = pygame.Surface((18, 18), pygame.SRCALPHA)
            ship.fill((255, 0, 180, 255))

        army = Army(Country.BLUE, UnitType.SWORDSMAN, 2)
        army.embarked = True
        surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        draw_army_badge(surf, 0, 0, army, assets=Assets())
        self.assertEqual(surf.get_at((CELL_SIZE // 2, CELL_SIZE // 2 - 1))[:3], (255, 0, 180))

    def test_asset_loader_reports_missing_unit_pngs(self):
        from asset_loader import AssetLoader

        pygame.display.set_mode((1, 1))
        loader = AssetLoader("assets")
        report = loader.summarize()
        self.assertIn("Spadassin", report)
        self.assertIn("Bateau", report)
        self.assertIsNotNone(loader.units[UnitType.SWORDSMAN])
        self.assertLess(loader.units[UnitType.SWORDSMAN].get_at((0, 0))[3], 40)
        self.assertIsNone(loader.units[UnitType.SPEARMAN])
        self.assertIsNone(loader.ship)

    def test_knockout_keeps_dark_gray_art(self):
        from asset_loader import AssetLoader

        pygame.display.set_mode((1, 1))
        loader = AssetLoader("assets")
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        for x in range(32):
            for y in range(32):
                if x < 4 or y < 4 or x > 27 or y > 27:
                    surf.set_at((x, y), (0, 0, 0, 255))
        for x in range(8, 24):
            for y in range(8, 24):
                surf.set_at((x, y), (83, 83, 83, 255))
        out = loader._knockout_black_background(surf)
        self.assertEqual(out.get_at((0, 0))[3], 0)
        self.assertEqual(out.get_at((16, 16))[:3], (83, 83, 83))
        self.assertEqual(out.get_at((16, 16))[3], 255)

    def test_knockout_does_not_eat_a_dark_horse(self):
        from asset_loader import AssetLoader

        pygame.display.set_mode((1, 1))
        loader = AssetLoader("assets")
        surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        for x in range(14, 34):
            for y in range(18, 38):
                surf.set_at((x, y), (12, 12, 12, 255))
        out = loader._knockout_black_background(surf)
        self.assertEqual(out.get_at((0, 0))[3], 0)
        self.assertEqual(out.get_at((24, 28))[:3], (12, 12, 12))
        self.assertEqual(out.get_at((24, 28))[3], 255)

    def test_cavalry_png_keeps_gray_without_stretching(self):
        from asset_loader import AssetLoader

        pygame.display.set_mode((1, 1))
        loader = AssetLoader("assets")
        cavalry = loader.units[UnitType.CAVALRY]
        self.assertIsNotNone(cavalry)
        gray = 0
        for y in range(cavalry.get_height()):
            for x in range(cavalry.get_width()):
                color = cavalry.get_at((x, y))
                if color[3] > 80 and 50 <= color[0] <= 120 and abs(color[0] - color[1]) < 20:
                    gray += 1
        self.assertGreater(gray, 20)
        self.assertEqual(cavalry.get_width(), cavalry.get_height())

    def test_same_country_tiles_share_one_outer_border(self):
        grid = [[Cell(x, y) for y in range(GRID_ROWS)] for x in range(GRID_COLS)]
        for x in range(2, 5):
            for y in range(2, 5):
                grid[x][y].terrain = TerrainType.PLAIN
                grid[x][y].country = Country.RED
        grid[5][3].terrain = TerrainType.PLAIN
        grid[5][3].country = Country.BLUE
        inside = grid[3][3]
        edges = inside.political_edges(grid)
        self.assertEqual(edges["n"], "same")
        self.assertEqual(edges["s"], "same")
        self.assertEqual(edges["w"], "same")
        self.assertEqual(edges["e"], "same")
        west = grid[2][3]
        self.assertEqual(west.political_edges(grid)["w"], "outer")
        self.assertEqual(west.political_edges(grid)["e"], "same")
        east = grid[4][3]
        self.assertEqual(east.political_edges(grid)["e"], "frontier")
        self.assertEqual(east.territory_edge_kind(None), "outer")
        surf = pygame.Surface((CELL_SIZE * GRID_COLS, HUD_TOP + CELL_SIZE * GRID_ROWS))
        for x in range(2, 6):
            for y in range(2, 5):
                grid[x][y].draw(surf, grid=grid)


if __name__ == "__main__":
    unittest.main()
