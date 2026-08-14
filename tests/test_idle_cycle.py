"""Cycle N / Unité suivante — boucle de jeu accessible."""

import unittest

import pygame

from army import Army
from constants import Country, UnitType, WINDOW_WIDTH, WINDOW_HEIGHT
from test_naval_and_traits import make_stub_game
from ui import UI


class IdleCycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    def _two_idle_red_armies(self):
        game = make_stub_game()
        game.grid[0][0].army.movement_left = 0
        first = game.grid[2][2]
        first.country = Country.RED
        first.army = Army(Country.RED, UnitType.SWORDSMAN, 3)
        first.army.refresh_movement(game.players[Country.RED])
        second = game.grid[4][4]
        second.country = Country.RED
        second.army = Army(Country.RED, UnitType.CAVALRY, 2)
        second.army.refresh_movement(game.players[Country.RED])
        game.selected_cell = None
        return game, first, second

    def test_select_next_idle_cycles_then_wraps(self):
        game, first, second = self._two_idle_red_armies()
        self.assertTrue(game.select_next_idle_army())
        self.assertIs(game.selected_cell, first)
        self.assertTrue(game.select_next_idle_army())
        self.assertIs(game.selected_cell, second)
        self.assertTrue(game.select_next_idle_army())
        self.assertIs(game.selected_cell, first)

    def test_idle_list_skips_spent_and_foreign_armies(self):
        game = make_stub_game()
        game.grid[0][0].army.movement_left = 0
        spent = game.grid[2][2]
        spent.country = Country.RED
        spent.army = Army(Country.RED, UnitType.SWORDSMAN, 1)
        spent.army.movement_left = 0
        foreign = game.grid[3][3]
        foreign.army = Army(Country.BLUE, UnitType.SWORDSMAN, 2)
        foreign.army.movement_left = 3
        idle = game.grid[4][4]
        idle.country = Country.RED
        idle.army = Army(Country.RED, UnitType.SWORDSMAN, 1)
        idle.army.movement_left = 2
        self.assertEqual(game.idle_army_cells(Country.RED), [idle])

    def test_maybe_advance_keeps_army_with_moves(self):
        game, first, _second = self._two_idle_red_armies()
        game.selected_cell = first
        game.maybe_advance_after_orders()
        self.assertIs(game.selected_cell, first)

    def test_maybe_advance_jumps_when_spent(self):
        game, first, second = self._two_idle_red_armies()
        first.army.movement_left = 0
        game.selected_cell = first
        game.maybe_advance_after_orders()
        self.assertIs(game.selected_cell, second)

    def test_end_turn_button_cycles_idle_then_ends(self):
        ui = UI(pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)))
        game = make_stub_game()
        ui.layout(game)
        click = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": ui.btn_end_turn.rect.center}
        )
        self.assertEqual(ui.handle_event(click, game), "next_unit")

        game.grid[0][0].army.movement_left = 0
        ui.layout(game)
        self.assertEqual(ui.handle_event(click, game), "end_turn")


if __name__ == "__main__":
    unittest.main()
