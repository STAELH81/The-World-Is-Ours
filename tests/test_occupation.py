import unittest
from types import SimpleNamespace
from constants import Country
from main import Game


class OccupationLogicTests(unittest.TestCase):
    def test_partial_city_occupation_does_not_count(self):
        game = Game.__new__(Game)
        capital = SimpleNamespace(
            is_capital=True,
            is_city=False,
            capital_owner=Country.GREEN,
            city_owner=Country.NONE,
            country=Country.GREEN,
        )
        city = SimpleNamespace(
            is_capital=False,
            is_city=True,
            capital_owner=Country.NONE,
            city_owner=Country.GREEN,
            country=Country.RED,
        )
        game.grid = []

        urban = [capital, city]
        occupied = [c for c in urban if c.country not in (Country.GREEN, Country.NONE)]
        self.assertEqual(len(occupied), 1)
        self.assertNotEqual(len(occupied), len(urban))

    def test_all_urban_occupied_counts(self):
        capital = SimpleNamespace(
            is_capital=True,
            is_city=False,
            capital_owner=Country.GREEN,
            city_owner=Country.NONE,
            country=Country.RED,
        )
        city = SimpleNamespace(
            is_capital=False,
            is_city=True,
            capital_owner=Country.NONE,
            city_owner=Country.GREEN,
            country=Country.RED,
        )
        urban = [capital, city]
        occupied = [c for c in urban if c.country not in (Country.GREEN, Country.NONE)]
        self.assertEqual(len(occupied), len(urban))


if __name__ == "__main__":
    unittest.main()
