from constants import *


class Army:
    def __init__(self, country, unit_type, count=1):
        self.country = country
        self.unit_type = unit_type
        self.count = count
        self.has_moved = False
        self.movement_left = UNIT_MOVEMENT_RANGE.get(unit_type, MOVEMENT_RANGE)
        self.is_fortified = False
        self.embarked = False

    def movement_range(self, player=None):
        if self.embarked:
            return SHIP_MOVEMENT_RANGE
        base = UNIT_MOVEMENT_RANGE.get(self.unit_type, MOVEMENT_RANGE)
        if player is not None and self.unit_type == UnitType.CAVALRY:
            base += getattr(player, "cavalry_move_bonus", 0)
        return base

    def refresh_movement(self, player=None):
        self.has_moved = False
        self.movement_left = self.movement_range(player)

    def __repr__(self):
        ship = " navire" if self.embarked else ""
        return f"Army({COUNTRY_NAMES[self.country]}, {UNIT_NAMES[self.unit_type]}{ship}, x{self.count})"
