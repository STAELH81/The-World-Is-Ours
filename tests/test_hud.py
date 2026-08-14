import unittest

import pygame

from constants import (
    Country,
    HUD_TOP,
    TerrainType,
    UnitType,
    cell_screen_pos,
    screen_to_cell,
)
from test_naval_and_traits import make_stub_game
from ui import UI


class HudLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    def test_screen_to_cell_ignores_top_bar(self):
        self.assertIsNone(screen_to_cell(10, HUD_TOP - 1))
        self.assertEqual(screen_to_cell(1, HUD_TOP + 1), (0, 0))
        sx, sy = cell_screen_pos(3, 4)
        self.assertEqual(screen_to_cell(sx + 2, sy + 2), (3, 4))

    def test_bridge_only_on_coast_and_recruit_only_in_city(self):
        pygame.font.init()
        ui = UI(pygame.Surface((8, 8)))
        game = make_stub_game()
        inland = game.grid[5][5]
        inland.country = Country.RED
        game.selected_cell = inland
        ctx = ui.context(game)
        self.assertTrue(ctx["can_build_city"])
        self.assertFalse(ctx["can_build_bridge"])
        self.assertFalse(ctx["can_recruit"])

        game.grid[5][6].terrain = TerrainType.WATER
        game.grid[5][7].terrain = TerrainType.WATER
        game.grid[4][6].terrain = TerrainType.WATER
        game.grid[6][6].terrain = TerrainType.WATER
        ctx = ui.context(game)
        self.assertFalse(ctx["can_build_bridge"])

        game.grid[5][7].terrain = TerrainType.PLAIN
        ctx = ui.context(game)
        self.assertTrue(ctx["can_build_bridge"])

        city = game.grid[1][8]
        city.country = Country.RED
        city.is_city = True
        city.city_owner = Country.RED
        game.selected_cell = city
        ctx = ui.context(game)
        self.assertTrue(ctx["can_recruit"])
        self.assertFalse(ctx["can_build_city"])
        self.assertFalse(ctx["can_build_bridge"])
        self.assertEqual(len(ui.layout(game)[1]), 3)

    def test_selected_army_does_not_show_the_old_button_wall(self):
        pygame.font.init()
        ui = UI(pygame.Surface((8, 8)))
        game = make_stub_game()
        cell = game.grid[4][8]
        cell.country = Country.RED
        cell.terrain = TerrainType.PLAIN
        from army import Army

        cell.army = Army(Country.RED, UnitType.CAVALRY, 1)
        cell.army.refresh_movement(game.players[Country.RED])
        game.selected_cell = cell
        ctx, buttons = ui.layout(game)
        self.assertTrue(ctx["can_fortify"])
        self.assertEqual([b.text for b in buttons], ["Fortifier"])

    def test_tooltip_wraps_long_kingdom_names(self):
        pygame.font.init()
        from theme import load_font, wrap_text

        font = load_font(16)
        lines = wrap_text(font, "Royaume Rouge  (10,13)", 240)
        self.assertGreaterEqual(len(lines), 1)
        for line in lines:
            self.assertLessEqual(font.size(line)[0], 240)


if __name__ == "__main__":
    unittest.main()
