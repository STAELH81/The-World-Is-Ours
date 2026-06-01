import unittest
from cell import Cell
from constants import GRID_COLS, GRID_ROWS, Country, TerrainType
from map_generator import MapGenerator, PLAYABLE_COUNTRIES


class StubGame:
    def __init__(self):
        self.grid = [[Cell(x, y) for y in range(GRID_ROWS)] for x in range(GRID_COLS)]
        self.map_seed = None

    def apply_country(self, coords, country):
        for x, y in coords:
            self.grid[x][y].country = country

    def add_beaches(self):
        pass

    def place_capitals_from_dict(self, capitals):
        for country, (x, y) in capitals.items():
            self.grid[x][y].is_capital = True
            self.grid[x][y].capital_owner = country


class MapGeneratorTests(unittest.TestCase):
    def test_generates_five_balanced_islands(self):
        game = StubGame()
        MapGenerator(seed=123).generate(game)

        sizes = []
        for country in PLAYABLE_COUNTRIES:
            count = sum(
                1
                for x in range(GRID_COLS)
                for y in range(GRID_ROWS)
                if game.grid[x][y].country == country
            )
            sizes.append(count)
            self.assertGreaterEqual(count, 40)

        self.assertEqual(len(sizes), 5)
        self.assertLessEqual(max(sizes) - min(sizes), 12)

    def test_each_country_has_a_capital(self):
        game = StubGame()
        MapGenerator(seed=99).generate(game)
        for country in PLAYABLE_COUNTRIES:
            caps = [
                (x, y)
                for x in range(GRID_COLS)
                for y in range(GRID_ROWS)
                if game.grid[x][y].is_capital and game.grid[x][y].capital_owner == country
            ]
            self.assertEqual(len(caps), 1)


if __name__ == "__main__":
    unittest.main()
