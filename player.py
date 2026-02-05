from constants import *
from constants import GRID_COLS, GRID_ROWS, UNIT_UPKEEP
from constants import GRID_COLS, GRID_ROWS, UNIT_UPKEEP, UNIT_COSTS, COUNTRY_NAMES, CITY_TERRITORY_REQUIREMENT

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
    
    def count_cities(self, grid):
        """Compte le nombre de villes possédées"""
        cities = 0
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = grid[x][y]
                if cell.is_city and cell.country == self.country:
                    cities += 1
        return cities

    def count_territory(self, grid):
        """Compte le nombre de cases possédées"""
        territory = 0
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = grid[x][y]
                if cell.country == self.country:
                    territory += 1
        return territory

    def max_cities_allowed(self, grid):
        """Calcule le nombre maximum de villes autorisées"""
        territory = self.count_territory(grid)
        return territory // CITY_TERRITORY_REQUIREMENT