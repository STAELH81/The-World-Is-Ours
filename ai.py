import random
from constants import *

class AI:
    def __init__(self, game):
        self.game = game
    
    def play_turn(self, country):
        """Joue le tour pour un pays IA"""
        print(f"\n🤖 IA {COUNTRY_NAMES[country]} réfléchit...")
        
        player = self.game.players[country]
        
        # 1. Construction de ville si possible
        self.try_build_city(country, player)
        
        # 2. Recrutement d'unités
        self.recruit_units(country, player)
        
        # 3. Déplacement et attaque des armées
        self.move_armies(country)
        
        print(f"🤖 {COUNTRY_NAMES[country]} termine son tour")
    
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
                    cell.terrain not in [TerrainType.WATER, TerrainType.BEACH]):
                    
                    # Construit
                    player.spend_gold(CITY_COST)
                    cell.is_city = True
                    print(f"  🏘 Ville construite en ({x}, {y})")
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
        while player.gold >= 45 and recruited < 3:  # Max 3 unités par tour
            unit_type = random.choice([UnitType.SWORDSMAN, UnitType.CROSSBOWMAN, UnitType.CAVALRY])
            
            player.spend_gold(UNIT_COSTS[unit_type])
            
            if capital_cell.army and capital_cell.army.unit_type == unit_type:
                capital_cell.army.count += 1
            else:
                from army import Army
                capital_cell.army = Army(country, unit_type, 1)
            
            recruited += 1
        
        if recruited > 0:
            print(f"  ⚔️ {recruited} unité(s) recrutée(s)")
    
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
            
            # Cherche un ennemi à portée
            enemy = self.find_nearby_enemy(army_cell, country)
            
            if enemy:
                # Attaque !
                self.game.move_army(army_cell, enemy)
            else:
                # Bouge vers une case ennemie
                target = self.find_move_target(army_cell, country)
                if target:
                    self.game.move_army(army_cell, target)
    
    def find_nearby_enemy(self, from_cell, country):
        """Trouve un ennemi à portée d'attaque (3 cases)"""
        best_target = None
        best_distance = 999
        
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                
                # Case ennemie avec armée OU case ennemie sans armée
                if cell.country != Country.NONE and cell.country != country:
                    distance = abs(from_cell.x - x) + abs(from_cell.y - y)
                    
                    if distance <= MOVEMENT_RANGE and distance < best_distance:
                        # Priorité : attaquer les armées
                        if cell.army:
                            best_target = cell
                            best_distance = distance
                        elif not best_target:  # Sinon conquérir terrain vide
                            best_target = cell
                            best_distance = distance
        
        return best_target
    
    def find_move_target(self, from_cell, country):
        """Trouve une case où se déplacer (vers ennemi le plus proche)"""
        # Cherche la case ennemie la plus proche
        closest_enemy = None
        closest_distance = 999
        
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                if cell.country != Country.NONE and cell.country != country:
                    distance = abs(from_cell.x - x) + abs(from_cell.y - y)
                    if distance < closest_distance:
                        closest_enemy = cell
                        closest_distance = distance
        
        if not closest_enemy:
            return None
        
        # Trouve la meilleure case pour se rapprocher
        best_move = None
        best_distance = closest_distance
        
        # Teste les 4 directions
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x = from_cell.x + dx
            new_y = from_cell.y + dy
            
            if 0 <= new_x < GRID_COLS and 0 <= new_y < GRID_ROWS:
                target_cell = self.game.grid[new_x][new_y]
                
                # Peut se déplacer si : neutre OU allié OU ennemi
                if target_cell.terrain != TerrainType.WATER:
                    distance = abs(new_x - closest_enemy.x) + abs(new_y - closest_enemy.y)
                    
                    if distance < best_distance:
                        best_move = target_cell
                        best_distance = distance
        
        return best_move