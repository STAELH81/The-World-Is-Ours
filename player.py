from constants import *
from constants import GRID_COLS, GRID_ROWS, UNIT_UPKEEP, UNIT_COSTS, COUNTRY_NAMES, CITY_TERRITORY_REQUIREMENT

class Player:
    def __init__(self, country):
        self.country = country
        self.gold = 500  # Or de départ
        self.is_ai = False  # Pour différencier joueur humain et IA
        self.unlocked_techs = []
        self.city_income_bonus = 0
        self.bridge_hp_bonus = 0
        self.bridge_cost_reduction = 0
        self.ranged_range_bonus = 0
        self.ranged_damage_bonus = 0
        self.upkeep_reduction = 0
    
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

        upkeep_per_unit = max(1, UNIT_UPKEEP - self.upkeep_reduction)
        return total_units * upkeep_per_unit
    
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

    def get_next_tech(self):
        if len(self.unlocked_techs) >= len(TECH_TREE):
            return None
        return TECH_TREE[len(self.unlocked_techs)]

    def can_research_next(self):
        tech = self.get_next_tech()
        return tech is not None and self.gold >= tech["cost"]

    def research_next(self):
        tech = self.get_next_tech()
        if tech is None or self.gold < tech["cost"]:
            return None
        self.gold -= tech["cost"]
        self.unlocked_techs.append(tech["id"])

        if tech["id"] == "economy":
            self.city_income_bonus += 30
        elif tech["id"] == "engineering":
            self.bridge_hp_bonus += 1
            self.bridge_cost_reduction += 20
        elif tech["id"] == "ballistics":
            self.ranged_range_bonus += 1
            self.ranged_damage_bonus += 1
        elif tech["id"] == "logistics":
            self.upkeep_reduction += 1
        return tech