from constants import *

class Army:
    def __init__(self, country, unit_type, count=1):
        self.country = country
        self.unit_type = unit_type
        self.count = count  # Nombre d'unités dans cette armée
        self.has_moved = False
        self.movement_left = UNIT_MOVEMENT_RANGE.get(unit_type, MOVEMENT_RANGE)
        self.is_fortified = False
    
    def __repr__(self):
        return f"Army({COUNTRY_NAMES[self.country]}, {UNIT_NAMES[self.unit_type]}, x{self.count})"