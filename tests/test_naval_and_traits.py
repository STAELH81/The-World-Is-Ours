import unittest
from unittest.mock import MagicMock

from army import Army
from cell import Cell
from constants import (
    CAPITAL_INCOME,
    CITY_INCOME,
    Country,
    EMBARK_COST,
    GRID_COLS,
    GRID_ROWS,
    TerrainType,
    UNIT_COSTS,
    UNIT_MOVEMENT_RANGE,
    UnitType,
)
from main import Game
from player import Player


class DummyFx:
    def is_busy(self):
        return False

    def clear(self):
        pass

    def float_text(self, *args, **kwargs):
        pass

    def show_banner(self, *args, **kwargs):
        pass

    def start_walk(self, origin_cell, path_cells, army, on_done, ticks_per_cell=7):
        if on_done:
            on_done()


def make_stub_game():
    game = Game.__new__(Game)
    game.grid = [[Cell(x, y) for y in range(GRID_ROWS)] for x in range(GRID_COLS)]
    for x in range(GRID_COLS):
        for y in range(GRID_ROWS):
            cell = game.grid[x][y]
            cell.terrain = TerrainType.PLAIN
            cell.country = Country.NONE
    game.players = {
        Country.RED: Player(Country.RED),
        Country.GREEN: Player(Country.GREEN),
        Country.BLUE: Player(Country.BLUE),
        Country.YELLOW: Player(Country.YELLOW),
        Country.ORANGE: Player(Country.ORANGE),
    }
    game.current_player_country = Country.RED
    game.turn_number = 1
    game.game_mode = "solo"
    game.winner_country = None
    game.player_defeated = False
    game.game_over_message = ""
    game.defeated_countries = set()
    game.last_aggressor = {}
    game.gold_looted = {}
    game.occupation_tracker = {}
    game.event_log = []
    game.animations = []
    game.visibility = {(x, y) for x in range(GRID_COLS) for y in range(GRID_ROWS)}
    game.selected_cell = None
    game.selected_army_cell = None
    game.move_targets = set()
    game.attack_targets = set()
    game.ranged_targets = set()
    game.embark_targets = set()
    game.disembark_targets = set()
    game.bridge_mode = False
    game.bridge_targets = set()
    game.ranged_mode = False
    game.preview_path_cells = []
    game.audio = MagicMock()
    game.fx = DummyFx()
    game.last_income = 0
    game.last_upkeep = 0
    game.ai_turn_pending = False

    # Keep every kingdom alive so move/combat helpers do not annex empty foes.
    for index, country in enumerate(
        [Country.RED, Country.GREEN, Country.BLUE, Country.YELLOW, Country.ORANGE]
    ):
        cell = game.grid[0][index]
        cell.country = country
        cell.is_capital = True
        cell.capital_owner = country
        cell.army = Army(country, UnitType.SWORDSMAN, 1)
        cell.army.refresh_movement(game.players[country])
    return game


class NavalAndTraitTests(unittest.TestCase):
    def test_embark_sail_and_land_disembark(self):
        game = make_stub_game()
        land = game.grid[8][8]
        beach = game.grid[8][9]
        water = game.grid[8][10]
        inland = game.grid[7][10]

        land.terrain = TerrainType.PLAIN
        land.country = Country.RED
        land.army = Army(Country.RED, UnitType.CAVALRY, 1)
        land.army.refresh_movement(game.players[Country.RED])
        beach.terrain = TerrainType.BEACH
        water.terrain = TerrainType.WATER
        inland.terrain = TerrainType.PLAIN

        self.assertNotIn((beach.x, beach.y), game.get_embark_targets(land))
        self.assertNotIn((water.x, water.y), game.get_embark_targets(land))

        game.move_army(land, beach)
        self.assertIsNotNone(beach.army)
        self.assertFalse(beach.army.embarked)
        self.assertEqual(game.players[Country.RED].gold, 500)

        beach.army.refresh_movement(game.players[Country.RED])
        self.assertIn((water.x, water.y), game.get_embark_targets(beach))
        self.assertTrue(game.embark_army(beach, water))
        self.assertIsNone(beach.army)
        self.assertTrue(water.army.embarked)
        self.assertEqual(game.players[Country.RED].gold, 500 - game.players[Country.RED].embark_cost())

        water.army.refresh_movement(game.players[Country.RED])
        self.assertIn((inland.x, inland.y), game.get_disembark_targets(water))
        self.assertTrue(game.disembark_army(water, inland))
        self.assertIsNone(water.army)
        self.assertFalse(inland.army.embarked)

    def test_walking_on_beach_does_not_embark(self):
        game = make_stub_game()
        land = game.grid[8][8]
        beach = game.grid[8][9]
        land.terrain = TerrainType.PLAIN
        land.country = Country.RED
        land.army = Army(Country.RED, UnitType.CAVALRY, 1)
        land.army.refresh_movement(game.players[Country.RED])
        beach.terrain = TerrainType.BEACH
        gold = game.players[Country.RED].gold
        game.request_move(land, beach, animate=False)
        self.assertIsNone(land.army)
        self.assertFalse(beach.army.embarked)
        self.assertEqual(game.players[Country.RED].gold, gold)

    def test_disembark_from_water_onto_beach(self):
        game = make_stub_game()
        water = game.grid[6][6]
        beach = game.grid[6][7]
        water.terrain = TerrainType.WATER
        beach.terrain = TerrainType.BEACH
        water.army = Army(Country.RED, UnitType.SWORDSMAN, 2)
        water.army.embarked = True
        water.army.refresh_movement(game.players[Country.RED])

        self.assertIn((beach.x, beach.y), game.get_disembark_targets(water))
        self.assertTrue(game.disembark_army(water, beach))
        self.assertIsNone(water.army)
        self.assertFalse(beach.army.embarked)

    def test_ship_cannot_walk_inland_without_disembark(self):
        game = make_stub_game()
        water = game.grid[5][5]
        inland = game.grid[5][6]
        water.terrain = TerrainType.WATER
        inland.terrain = TerrainType.PLAIN
        water.army = Army(Country.RED, UnitType.CAVALRY, 1)
        water.army.embarked = True
        water.army.refresh_movement(game.players[Country.RED])

        game.move_army(water, inland)
        self.assertIs(water.army, game.grid[5][5].army)
        self.assertTrue(water.army.embarked)
        self.assertIsNone(inland.army)

    def test_bridge_only_on_strait_not_along_beach(self):
        game = make_stub_game()
        left = game.grid[4][10]
        water = game.grid[5][10]
        right = game.grid[6][10]
        coast_water = game.grid[5][11]
        beach = game.grid[5][9]
        left.terrain = TerrainType.PLAIN
        left.country = Country.RED
        right.terrain = TerrainType.PLAIN
        water.terrain = TerrainType.WATER
        beach.terrain = TerrainType.BEACH
        beach.country = Country.RED
        coast_water.terrain = TerrainType.WATER
        game.grid[4][11].terrain = TerrainType.WATER
        game.grid[6][11].terrain = TerrainType.WATER
        game.grid[5][12].terrain = TerrainType.WATER

        self.assertTrue(game.is_valid_bridge_site(water))
        self.assertFalse(game.is_valid_bridge_site(coast_water))
        self.assertFalse(game.is_valid_bridge_site(beach))
        self.assertTrue(game.build_bridge_on_cell(water))
        self.assertEqual(water.terrain, TerrainType.BRIDGE)
        self.assertFalse(game.is_valid_bridge_site(coast_water))

    def test_friendly_city_merge_does_not_destroy_army(self):
        game = make_stub_game()
        city = game.grid[4][10]
        neighbor = game.grid[4][11]
        city.terrain = TerrainType.PLAIN
        neighbor.terrain = TerrainType.PLAIN
        city.country = Country.RED
        neighbor.country = Country.RED
        city.is_city = True
        city.city_owner = Country.RED
        city.army = Army(Country.RED, UnitType.CAVALRY, 2)
        city.army.refresh_movement(game.players[Country.RED])
        neighbor.army = Army(Country.RED, UnitType.CAVALRY, 1)
        neighbor.army.refresh_movement(game.players[Country.RED])

        game.move_army(neighbor, city)
        self.assertIsNone(neighbor.army)
        self.assertIsNotNone(city.army)
        self.assertEqual(city.army.count, 3)
        self.assertEqual(city.army.country, Country.RED)

    def test_red_swords_are_cheaper_and_hit_harder(self):
        red = Player(Country.RED)
        green = Player(Country.GREEN)
        self.assertEqual(red.unit_cost(UnitType.SWORDSMAN), UNIT_COSTS[UnitType.SWORDSMAN] - 10)
        self.assertEqual(green.unit_cost(UnitType.SWORDSMAN), UNIT_COSTS[UnitType.SWORDSMAN])

        game = make_stub_game()
        attacker = game.grid[3][8]
        defender = game.grid[3][9]
        attacker.terrain = TerrainType.PLAIN
        defender.terrain = TerrainType.PLAIN
        attacker.army = Army(Country.RED, UnitType.SWORDSMAN, 1)
        defender.army = Army(Country.GREEN, UnitType.SWORDSMAN, 1)
        attacker.army.refresh_movement(game.players[Country.RED])
        result = game.battle(attacker, defender)
        # Sans le +1 d'attaque rouge, 3 vs 4 ferait gagner le défenseur.
        self.assertEqual(result["winner"], "draw")

    def test_blue_cheaper_navy_and_orange_cavalry_range(self):
        blue = Player(Country.BLUE)
        orange = Player(Country.ORANGE)
        self.assertEqual(blue.embark_cost(), max(10, EMBARK_COST - 20))
        cavalry = Army(Country.ORANGE, UnitType.CAVALRY, 1)
        self.assertEqual(
            cavalry.movement_range(orange),
            UNIT_MOVEMENT_RANGE[UnitType.CAVALRY] + 1,
        )

    def test_yellow_capital_income_and_green_city_bonus(self):
        game = make_stub_game()
        yellow = game.players[Country.YELLOW]
        green = game.players[Country.GREEN]
        start_yellow = yellow.gold
        game.current_player_country = Country.YELLOW
        game.generate_income()
        expected = CAPITAL_INCOME + yellow.capital_income_bonus - yellow.calculate_upkeep(game.grid)
        self.assertEqual(yellow.gold, start_yellow + expected)

        city = game.grid[2][10]
        city.is_city = True
        city.city_owner = Country.GREEN
        city.country = Country.GREEN
        start_green = green.gold
        game.current_player_country = Country.GREEN
        game.generate_income()
        expected_green = (
            CAPITAL_INCOME
            + CITY_INCOME
            + green.city_income_bonus
            - green.calculate_upkeep(game.grid)
        )
        self.assertEqual(green.gold, start_green + expected_green)

    def test_green_forest_defense_bonus(self):
        game = make_stub_game()
        attacker = game.grid[9][9]
        defender = game.grid[9][10]
        attacker.terrain = TerrainType.PLAIN
        defender.terrain = TerrainType.FOREST
        attacker.army = Army(Country.RED, UnitType.SWORDSMAN, 3)
        defender.army = Army(Country.GREEN, UnitType.SWORDSMAN, 2)
        result = game.battle(attacker, defender)
        # Sans le +1 forêt vert : 12 vs 10 (attaquant). Avec le bonus : 12 vs 12.
        self.assertEqual(result["winner"], "draw")

    def test_selecting_crossbowman_fills_ranged_targets(self):
        game = make_stub_game()
        bow = game.grid[11][11]
        foe = game.grid[11][13]
        bow.terrain = TerrainType.PLAIN
        foe.terrain = TerrainType.PLAIN
        bow.army = Army(Country.RED, UnitType.CROSSBOWMAN, 1)
        bow.army.refresh_movement(game.players[Country.RED])
        foe.army = Army(Country.ORANGE, UnitType.SWORDSMAN, 1)
        game.select_army_for_orders(bow)
        self.assertIn((foe.x, foe.y), game.ranged_targets)

    def test_city_cannot_recruit_twice_same_turn(self):
        game = make_stub_game()
        city = game.grid[1][8]
        city.terrain = TerrainType.PLAIN
        city.country = Country.RED
        city.is_city = True
        city.city_owner = Country.RED
        game.selected_cell = city
        game.players[Country.RED].gold = 500
        game.recruit_unit(UnitType.CAVALRY)
        self.assertEqual(city.army.count, 1)
        gold_after = game.players[Country.RED].gold
        game.recruit_unit(UnitType.CAVALRY)
        self.assertEqual(city.army.count, 1)
        self.assertEqual(game.players[Country.RED].gold, gold_after)

    def test_indecisive_combat_spends_attacker_movement(self):
        game = make_stub_game()
        game.current_player_country = Country.GREEN
        attacker = game.grid[8][8]
        defender = game.grid[8][9]
        attacker.terrain = TerrainType.PLAIN
        defender.terrain = TerrainType.PLAIN
        attacker.country = Country.GREEN
        defender.country = Country.YELLOW
        attacker.army = Army(Country.GREEN, UnitType.SWORDSMAN, 4)
        defender.army = Army(Country.YELLOW, UnitType.SWORDSMAN, 3)
        attacker.army.refresh_movement(game.players[Country.GREEN])
        defender.army.refresh_movement(game.players[Country.YELLOW])
        game.move_army(attacker, defender)
        self.assertIsNotNone(attacker.army)
        self.assertIsNotNone(defender.army)
        self.assertEqual(attacker.army.country, Country.GREEN)
        self.assertEqual(attacker.army.movement_left, 0)
        self.assertTrue(attacker.army.has_moved)
        self.assertEqual(attacker.army.count, 3)
        self.assertEqual(defender.army.count, 2)


if __name__ == "__main__":
    unittest.main()
