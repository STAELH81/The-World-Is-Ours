from constants import *


class Player:
    def __init__(self, country):
        self.country = country
        self.gold = 500
        self.is_ai = False
        self.unlocked_techs = []
        self.city_income_bonus = 0
        self.bridge_hp_bonus = 0
        self.bridge_cost_reduction = 0
        self.ranged_range_bonus = 0
        self.ranged_damage_bonus = 0
        self.upkeep_reduction = 0
        self.swordsman_cost_reduction = 0
        self.swordsman_attack_bonus = 0
        self.embark_cost_reduction = 0
        self.forest_defense_bonus = 0
        self.capital_income_bonus = 0
        self.cavalry_move_bonus = 0
        self.apply_kingdom_trait()

    def apply_kingdom_trait(self):
        trait = KINGDOM_TRAITS.get(self.country)
        if not trait:
            return
        self.swordsman_cost_reduction = trait.get("swordsman_cost_reduction", 0)
        self.swordsman_attack_bonus = trait.get("swordsman_attack_bonus", 0)
        self.bridge_cost_reduction = trait.get("bridge_cost_reduction", 0)
        self.embark_cost_reduction = trait.get("embark_cost_reduction", 0)
        self.forest_defense_bonus = trait.get("forest_defense_bonus", 0)
        self.city_income_bonus = trait.get("city_income_bonus", 0)
        self.capital_income_bonus = trait.get("capital_income_bonus", 0)
        self.cavalry_move_bonus = trait.get("cavalry_move_bonus", 0)

    def trait_info(self):
        return KINGDOM_TRAITS.get(self.country)

    def unit_cost(self, unit_type):
        cost = UNIT_COSTS[unit_type]
        if unit_type == UnitType.SWORDSMAN:
            cost = max(10, cost - self.swordsman_cost_reduction)
        return cost

    def embark_cost(self):
        return max(10, EMBARK_COST - self.embark_cost_reduction)

    def bridge_cost(self):
        return max(40, BRIDGE_COST - self.bridge_cost_reduction)

    def add_gold(self, amount):
        self.gold += amount

    def spend_gold(self, amount):
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def can_afford(self, unit_type):
        return self.gold >= self.unit_cost(unit_type)

    def __repr__(self):
        return f"Player({COUNTRY_NAMES[self.country]}, {self.gold} or)"

    def calculate_upkeep(self, grid):
        total_units = 0
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = grid[x][y]
                if cell.army and cell.army.country == self.country:
                    total_units += cell.army.count
        upkeep_per_unit = max(1, UNIT_UPKEEP - self.upkeep_reduction)
        return total_units * upkeep_per_unit

    def count_cities(self, grid):
        cities = 0
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = grid[x][y]
                if cell.is_city and cell.country == self.country:
                    cities += 1
        return cities

    def count_territory(self, grid):
        territory = 0
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                if grid[x][y].country == self.country:
                    territory += 1
        return territory

    def max_cities_allowed(self, grid):
        return self.count_territory(grid) // CITY_TERRITORY_REQUIREMENT

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
