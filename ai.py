import random
from constants import *
from army import Army

class AI:
    def __init__(self, game):
        self.game = game

    def is_target_allowed(self, attacker_country, target_country):
        """Soft truce in solo: AI avoids hard focus on RED early game."""
        if target_country == Country.NONE:
            return False
        if (
            self.game.game_mode == "solo"
            and attacker_country != Country.RED
            and target_country == Country.RED
            and self.game.turn_number <= 3
        ):
            return False
        return True
    
    def play_turn(self, country):
        """Joue le tour pour un pays IA"""
        print(f"\n[AI] {COUNTRY_NAMES[country]} réfléchit...")
        
        player = self.game.players[country]
        if player.can_research_next() and player.gold >= player.get_next_tech()["cost"] + 120:
            tech = player.research_next()
            if tech:
                self.game.log_event(f"[TECH] {COUNTRY_NAMES[country]} debloque {tech['name']}")
        
        # 1. Construction de ville si possible
        self.try_build_city(country, player)
        
        # 2. Recrutement d'unités
        self.recruit_units(country, player)
        
        # 3. Déplacement et attaque des armées
        self.move_armies(country)
        
        print(f"[AI] {COUNTRY_NAMES[country]} termine son tour")
    
    def try_build_city(self, country, player):
        """Tente de construire une ville"""
        if player.gold < CITY_COST:
            return
        
        current_cities = player.count_cities(self.game.grid)
        max_cities = player.max_cities_allowed(self.game.grid)
        
        if current_cities >= max_cities:
            return
        
        # Trouve une case valide pour construire
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                
                if (cell.country == country and 
                    not cell.is_capital and 
                    not cell.is_city and
                    cell.terrain not in [TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE]):
                    # Construit
                    player.spend_gold(CITY_COST)
                    cell.is_city = True
                    cell.city_owner = country
                    print(f"  [CITY] Ville construite en ({x}, {y})")
                    return
    
    def recruit_units(self, country, player):
        """Recrute des unités sur la capitale"""
        # Trouve la capitale
        capital_cell = None
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                if cell.is_capital and cell.country == country:
                    capital_cell = cell
                    break
            if capital_cell:
                break
        
        if not capital_cell:
            return
        
        # Recrute tant qu'il y a de l'or
        recruited = 0
        min_unit_cost = min(UNIT_COSTS.values())
        while player.gold >= min_unit_cost and recruited < 1:  # Max 1 recrutement par centre urbain / tour
            if capital_cell.last_recruit_turn == self.game.turn_number:
                break
            # If a capital army already exists, keep stacking that type.
            # This avoids replacing an existing army with another type.
            if capital_cell.army:
                unit_type = capital_cell.army.unit_type
            else:
                affordable_types = [u for u in UNIT_COSTS if player.gold >= UNIT_COSTS[u]]
                if not affordable_types:
                    break
                unit_type = random.choice(affordable_types)
            
            player.spend_gold(UNIT_COSTS[unit_type])
            
            if capital_cell.army:
                if capital_cell.army.count >= MAX_UNITS_PER_ARMY:
                    break
                capital_cell.army.count += 1
            else:
                capital_cell.army = Army(country, unit_type, 1)
            capital_cell.last_recruit_turn = self.game.turn_number
            
            recruited += 1
        
        if recruited > 0:
            print(f"  [ARMY] {recruited} unité(s) recrutée(s)")
    
    def move_armies(self, country):
        """Déplace et attaque avec les armées"""
        # Liste toutes les armées du pays
        armies = []
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                if cell.army and cell.army.country == country:
                    armies.append(cell)
        
        # Mélange pour varier les mouvements
        random.shuffle(armies)
        
        for army_cell in armies:
            # Vérifie si l'armée existe toujours (peut avoir été détruite en combat)
            if not army_cell.army:
                continue

            step_guard = 0
            while army_cell.army and army_cell.army.movement_left > 0 and step_guard < 3:
                step_guard += 1
                if army_cell.army.unit_type == UnitType.CROSSBOWMAN:
                    ranged_targets = self.game.get_ranged_targets(army_cell)
                    if ranged_targets:
                        tx, ty = random.choice(list(ranged_targets))
                        self.game.ranged_attack(army_cell, self.game.grid[tx][ty])
                        continue
                enemy = self.find_nearby_enemy(army_cell, country)
                if enemy:
                    self.game.move_army(army_cell, enemy)
                else:
                    target = self.find_move_target(army_cell, country)
                    if target:
                        self.game.move_army(army_cell, target)
                    else:
                        break
    
    def find_nearby_enemy(self, from_cell, country):
        """Trouve un ennemi à portée d'attaque."""
        best_target = None
        best_distance = 999
        fallback_red_target = None
        fallback_red_distance = 999
        movement_range = from_cell.army.movement_left
        
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                
                # Case ennemie avec armée OU case ennemie sans armée
                if cell.country != Country.NONE and cell.country != country:
                    distance = abs(from_cell.x - x) + abs(from_cell.y - y)
                    
                    if distance <= movement_range and distance < best_distance:
                        if not self.is_target_allowed(country, cell.country):
                            if distance < fallback_red_distance:
                                fallback_red_target = cell
                                fallback_red_distance = distance
                            continue
                        # Priorité : attaquer les armées
                        if cell.army:
                            best_target = cell
                            best_distance = distance
                        elif not best_target:  # Sinon conquérir terrain vide
                            best_target = cell
                            best_distance = distance
        
        return best_target if best_target else fallback_red_target
    
    def find_move_target(self, from_cell, country):
        """Trouve une case où se déplacer (vers ennemi le plus proche)"""
        # Cherche la case ennemie la plus proche
        closest_enemy = None
        closest_distance = 999
        fallback_enemy = None
        fallback_distance = 999
        
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                if cell.country != Country.NONE and cell.country != country:
                    distance = abs(from_cell.x - x) + abs(from_cell.y - y)
                    if self.is_target_allowed(country, cell.country) and distance < closest_distance:
                        closest_enemy = cell
                        closest_distance = distance
                    elif distance < fallback_distance:
                        fallback_enemy = cell
                        fallback_distance = distance

        if not closest_enemy:
            closest_enemy = fallback_enemy
            closest_distance = fallback_distance
        
        if not closest_enemy:
            return None
        
        movement_range = from_cell.army.movement_left

        # Trouve la meilleure case pour se rapprocher
        best_move = None
        best_distance = closest_distance
        
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                distance_from_army = abs(from_cell.x - x) + abs(from_cell.y - y)
                if distance_from_army == 0 or distance_from_army > movement_range:
                    continue

                target_cell = self.game.grid[x][y]
                if target_cell.terrain == TerrainType.WATER:
                    continue
                if target_cell.army and target_cell.army.country == country:
                    if target_cell.army.unit_type != from_cell.army.unit_type:
                        continue

                distance_to_enemy = abs(x - closest_enemy.x) + abs(y - closest_enemy.y)
                if distance_to_enemy < best_distance:
                    best_move = target_cell
                    best_distance = distance_to_enemy
        
        return best_move