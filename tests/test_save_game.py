import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import pygame
import save_game
from constants import Country, TerrainType, UnitType, GRID_COLS, GRID_ROWS
from cell import Cell
from army import Army


class SaveGameTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.tmp = tempfile.TemporaryDirectory()
        self.save_path = os.path.join(self.tmp.name, "test_save.json")
        self.original_path = save_game.SAVE_PATH
        save_game.SAVE_PATH = self.save_path

    def tearDown(self):
        save_game.SAVE_PATH = self.original_path
        self.tmp.cleanup()

    def _minimal_game(self):
        game = MagicMock()
        game.game_mode = "solo"
        game.turn_number = 2
        game.current_player_country = Country.RED
        game.winner_country = None
        game.player_defeated = False
        game.game_over_message = ""
        game.defeated_countries = set()
        game.last_aggressor = {Country.GREEN: Country.RED}
        game.map_seed = 42
        game.last_income = 100
        game.last_upkeep = 20
        game.event_log = ["test"]
        game.settings = {"volume": 0.5, "ai_speed": "fast", "difficulty": "easy"}

        game.grid = [[Cell(x, y) for y in range(GRID_ROWS)] for x in range(GRID_COLS)]
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = game.grid[x][y]
                cell.terrain = TerrainType.PLAIN
                cell.country = Country.RED if x < GRID_COLS // 2 else Country.GREEN
                cell.is_capital = x == 3 and y == 3
                cell.is_city = False
                cell.bridge_hp = 0
                cell.capital_owner = Country.RED if cell.is_capital else Country.NONE
                cell.city_owner = Country.NONE
                cell.last_recruit_turn = -1
                cell.discovered_by = {Country.RED}
                if x == 0 and y == 0:
                    cell.army = Army(Country.RED, UnitType.SWORDSMAN, 2)

        from player import Player

        game.players = {
            Country.RED: Player(Country.RED),
            Country.GREEN: Player(Country.GREEN),
            Country.BLUE: Player(Country.BLUE),
            Country.YELLOW: Player(Country.YELLOW),
            Country.ORANGE: Player(Country.ORANGE),
        }
        game.players[Country.RED].gold = 500
        game.players[Country.GREEN].gold = 300
        game.players[Country.GREEN].is_ai = True
        game.players[Country.BLUE].is_ai = True
        game.players[Country.YELLOW].is_ai = True
        game.players[Country.ORANGE].is_ai = True
        game.gold_looted = {Country.RED: 18}
        game.grid[0][0].army.embarked = True
        return game

    def test_save_and_load_roundtrip(self):
        game = self._minimal_game()
        self.assertTrue(save_game.save_game(game))

        loaded = MagicMock()
        loaded.screen = MagicMock()
        loaded.state = "menu"
        loaded.audio = MagicMock()

        self.assertTrue(save_game.load_game(loaded))
        self.assertEqual(loaded.turn_number, 2)
        self.assertEqual(loaded.current_player_country, Country.RED)
        self.assertEqual(loaded.grid[0][0].army.count, 2)
        self.assertTrue(loaded.grid[0][0].army.embarked)
        self.assertTrue(loaded.grid[3][3].is_capital)
        self.assertEqual(loaded.settings["difficulty"], "easy")
        self.assertEqual(loaded.gold_looted[Country.RED], 18)
        self.assertEqual(loaded.players[Country.RED].swordsman_cost_reduction, 10)
        self.assertEqual(len(loaded.players), 5)

    def test_invalid_version_rejected(self):
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump({"version": 999}, f)
        loaded = MagicMock()
        loaded.screen = MagicMock()
        loaded.audio = MagicMock()
        self.assertFalse(save_game.load_game(loaded))

    def test_legacy_v1_save_rejected(self):
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "grid": []}, f)
        loaded = MagicMock()
        loaded.screen = MagicMock()
        loaded.audio = MagicMock()
        self.assertFalse(save_game.load_game(loaded))

    def test_corrupt_json_rejected(self):
        with open(self.save_path, "w", encoding="utf-8") as f:
            f.write("{not-json")
        loaded = MagicMock()
        loaded.screen = MagicMock()
        loaded.audio = MagicMock()
        self.assertFalse(save_game.load_game(loaded))


if __name__ == "__main__":
    unittest.main()
