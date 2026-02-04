from constants import *
from constants import GRID_COLS, GRID_ROWS, UNIT_UPKEEP

class Player:
    def __init__(self, country):
        self.country = country
        self.gold = 500  # Or de départ
        self.is_ai = False  # Pour différencier joueur humain et IA
    
    def add_gold(self, amount):
        self.gold += amount
    
    def spend_gold(self, amount):
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
    
    def can_afford(self, unit_type):
        return self.gold >= UNIT_COSTS[unit_type]
    
    def __repr__(self):
        return f"Player({COUNTRY_NAMES[self.country]}, {self.gold} or)"
    
    def calculate_upkeep(self, grid):
        """Calcule le coût d'entretien total des armées"""
        total_units = 0
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = grid[x][y]
                if cell.army and cell.army.country == self.country:
                    total_units += cell.army.count

        return total_units * UNIT_UPKEEP