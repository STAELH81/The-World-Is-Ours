import pygame
import sys
from collections import deque
from constants import *
from cell import Cell
from ui import UI
from menu import Menu
from army import Army
from player import Player
from ai import AI
from asset_loader import AssetLoader


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("The World Is Ours")
        self.clock = pygame.time.Clock()
        self.running = True
        self.assets = AssetLoader("assets")
        
        # États du jeu
        self.state = "menu"  # menu, playing
        self.game_mode = None  # solo, godgame
        
        # Menu
        self.menu = Menu(self.screen)
        
        # Grille de cellules (sera initialisée au démarrage du jeu)
        self.grid = None
        self.selected_cell = None
        self.selected_army_cell = None  # Case with selected army for movement
        self.move_targets = set()
        self.attack_targets = set()
        self.ui = None

        # Joueurs
        self.players = {}
        self.current_player_country = Country.RED
        self.turn_number = 1

        self.ai = None  # Sera initialisé au démarrage
        self.winner_country = None
        self.visibility = set()
        self.event_log = []
        self.animations = []
        self.last_income = 0
        self.last_upkeep = 0
        self.bridge_mode = False
        self.bridge_targets = set()
        self.hovered_cell = None

    def start_game(self, mode):
        """Démarre une nouvelle partie"""
        self.game_mode = mode
        self.state = "playing"
        
        # Initialise le jeu
        self.grid = [[Cell(x, y) for y in range(GRID_ROWS)] for x in range(GRID_COLS)]
        self.selected_cell = None
        self.selected_army_cell = None
        self.move_targets.clear()
        self.attack_targets.clear()
        self.winner_country = None
        self.visibility.clear()
        self.event_log.clear()
        self.animations.clear()
        self.bridge_mode = False
        self.bridge_targets.clear()
        self.ui = UI(self.screen)

        self.ai = AI(self)
        
        # Génère la map
        self.generate_map()

        # Crée les joueurs
        self.init_players()
    
    def recruit_unit(self, unit_type):
        """Recrute une unité sur la case sélectionnée"""
        if not self.selected_cell:
            print("Aucune case sélectionnée")
            return

        cell = self.selected_cell
        player = self.players[self.current_player_country]

        # Vérifications
        if cell.country != self.current_player_country:
            print("Vous ne pouvez recruter que sur vos territoires")
            return

        if cell.terrain in (TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE):
            print("Impossible de recruter sur eau/plage/pont")
            return

        if not (cell.is_capital or cell.is_city):
            print("Le recrutement se fait uniquement dans une capitale ou une ville")
            return

        cost = UNIT_COSTS[unit_type]
        if not player.can_afford(unit_type):
            print(f"Pas assez d'or ! ({player.gold}/{cost})")
            return

        # Recrute
        player.spend_gold(cost)

        if cell.army and cell.army.unit_type == unit_type:
            # Ajoute à l'armée existante
            cell.army.count += 1
        else:
            # Crée une nouvelle armée (remplace l'ancienne si différente)
            cell.army = Army(self.current_player_country, unit_type, 1)

        self.log_event(f"[OK] {UNIT_NAMES[unit_type]} recrute. Or: {player.gold}")
    
    def build_city(self):
        """Construit une ville sur la case sélectionnée"""
        if not self.selected_cell:
            print("Aucune case sélectionnée")
            return

        cell = self.selected_cell
        player = self.players[self.current_player_country]

        # Vérifications
        if cell.country != self.current_player_country:
            print("Vous ne pouvez construire que sur vos territoires")
            return

        if cell.terrain in (TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE):
            print("Impossible de construire sur eau/plage/pont")
            return

        if cell.is_capital:
            print("Il y a déjà une capitale ici")
            return

        if cell.is_city:
            print("Il y a déjà une ville ici")
            return

        # Vérifie la limite de villes
        current_cities = player.count_cities(self.grid)
        max_cities = player.max_cities_allowed(self.grid)

        if current_cities >= max_cities:
            territory = player.count_territory(self.grid)
            print(f"Limite de villes atteinte ! ({current_cities}/{max_cities}) - Vous avez {territory} cases")
            return

        has_urban_support = False
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = cell.x + dx, cell.y + dy
            if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                neighbor = self.grid[nx][ny]
                if neighbor.country == self.current_player_country and (neighbor.is_city or neighbor.is_capital):
                    has_urban_support = True
                    break
        if not has_urban_support:
            print("Une ville doit etre adjacente a une ville/capitale alliee")
            return

        # Vérifie l'or
        if player.gold < CITY_COST:
            print(f"Pas assez d'or pour construire une ville ! ({player.gold}/{CITY_COST})")
            return

        # Construit
        player.spend_gold(CITY_COST)
        cell.is_city = True

        self.log_event(f"[OK] Ville construite. Or: {player.gold}")

    def move_army(self, from_cell, to_cell):
        """Déplace une armée d'une case à une autre"""
        if not from_cell.army:
            print("Pas d'armée à déplacer")
            return

        army = from_cell.army

        # Vérifications
        if army.country != self.current_player_country:
            print("Ce n'est pas votre armée")
            return
        if army.has_moved:
            self.log_event("Cette armee a deja bouge ce tour")
            return
        if army.movement_left <= 0:
            self.log_event("Cette armee n'a plus de mouvement")
            return

        if to_cell.terrain == TerrainType.WATER:
            self.log_event("Impossible de se deplacer sur l'eau")
            return
        if from_cell == to_cell:
            return

        # Calcul de distance (Manhattan)
        distance = abs(from_cell.x - to_cell.x) + abs(from_cell.y - to_cell.y)
        max_range = army.movement_left
        if distance > max_range:
            self.log_event(f"Trop loin ! Distance restante: {max_range}")
            return

        # Zone of control: if adjacent to an enemy army, you must engage nearby.
        engaged_targets = self.get_adjacent_enemy_cells(from_cell, self.current_player_country)
        if engaged_targets and (to_cell.x, to_cell.y) not in engaged_targets:
            self.log_event("Zone de controle: engage un ennemi adjacent")
            return

        path_cells = self.find_path(from_cell, to_cell, max_range, army)
        if not path_cells:
            self.log_event("Aucun chemin valide vers cette case")
            return
        move_cost = len(path_cells)

        # Si case ennemie avec armée → COMBAT
        if to_cell.army and to_cell.army.country != self.current_player_country:
            self.battle(from_cell, to_cell)
            if to_cell.army and to_cell.army.country == self.current_player_country:
                to_cell.army.movement_left = max(0, to_cell.army.movement_left - move_cost)
                to_cell.army.has_moved = to_cell.army.movement_left <= 0
                self.add_animation([(to_cell.x, to_cell.y)], (231, 76, 60), 16)
                self.apply_bridge_wear(path_cells)
            self.check_victory()
            return

        self.conquer_path(path_cells)

        # Si case ennemie vide → CONQUÊTE + DÉPLACEMENT
        if to_cell.country != Country.NONE and to_cell.country != self.current_player_country:
            self.log_event(f"[COMBAT] Conquete de {COUNTRY_NAMES[to_cell.country]}")
            to_cell.country = self.current_player_country

        # Déplacement simple
        if to_cell.army:
            # Fusion d'armées du même type
            if to_cell.army.unit_type == army.unit_type:
                to_cell.army.count += army.count
                to_cell.army.movement_left = max(0, to_cell.army.movement_left - move_cost)
                to_cell.army.has_moved = to_cell.army.movement_left <= 0
                from_cell.army = None
                self.log_event(f"[OK] Armees fusionnees ({to_cell.army.count})")
            else:
                self.log_event("Impossible de fusionner des unites differentes")
                return
        else:
            # Déplacement simple
            to_cell.army = army
            to_cell.army.movement_left = max(0, to_cell.army.movement_left - move_cost)
            to_cell.army.has_moved = to_cell.army.movement_left <= 0
            from_cell.army = None
            self.log_event("[OK] Deplacement effectue")
        self.add_animation([(from_cell.x, from_cell.y), (to_cell.x, to_cell.y)], (52, 152, 219), 14)
        self.apply_bridge_wear(path_cells)

        self.check_victory()

    def battle(self, attacker_cell, defender_cell):
        """Gère un combat entre deux armées"""
        attacker = attacker_cell.army
        defender = defender_cell.army

        self.log_event(f"[COMBAT] {COUNTRY_NAMES[attacker.country]} vs {COUNTRY_NAMES[defender.country]}")

        # Système RPS (Pierre-Papier-Ciseaux)
        # Spadassin > Arbalétrier > Cavalerie > Spadassin
        attacker_type = attacker.unit_type
        defender_type = defender.unit_type

        attacker_advantage = 0

        if attacker_type == UnitType.SWORDSMAN and defender_type == UnitType.CROSSBOWMAN:
            attacker_advantage = 1
        elif attacker_type == UnitType.CROSSBOWMAN and defender_type == UnitType.CAVALRY:
            attacker_advantage = 1
        elif attacker_type == UnitType.CAVALRY and defender_type == UnitType.SWORDSMAN:
            attacker_advantage = 1
        elif defender_type == UnitType.SWORDSMAN and attacker_type == UnitType.CROSSBOWMAN:
            attacker_advantage = -1
        elif defender_type == UnitType.CROSSBOWMAN and attacker_type == UnitType.CAVALRY:
            attacker_advantage = -1
        elif defender_type == UnitType.CAVALRY and attacker_type == UnitType.SWORDSMAN:
            attacker_advantage = -1

        # Bonus de terrain pour le défenseur
        terrain_bonus = TERRAIN_DEFENSE_BONUS[defender_cell.terrain]

        # Calcul des forces
        attacker_power = attacker.count * (UNIT_STATS[attacker_type]["attack"] + attacker_advantage)
        defender_power = defender.count * (UNIT_STATS[defender_type]["defense"] + terrain_bonus)

        print(f"  Force attaquant: {attacker_power} (avantage RPS: {attacker_advantage:+d})")
        print(f"  Force défenseur: {defender_power} (bonus terrain: +{terrain_bonus})")

        # Résolution
        if attacker_power > defender_power:
            # Victoire attaquant
            losses = max(1, defender.count // 2)  # L'attaquant perd 50% du défenseur
            attacker.count = max(1, attacker.count - losses)

            self.log_event(f"[OK] {COUNTRY_NAMES[attacker.country]} gagne ({losses} pertes)")

            # Conquête
            defender_cell.country = attacker.country
            defender_cell.army = attacker
            attacker_cell.army = None

        elif defender_power > attacker_power:
            # Victoire défenseur
            losses = max(1, attacker.count // 2)
            defender.count = max(1, defender.count - losses)

            self.log_event(f"[OK] {COUNTRY_NAMES[defender.country]} defend ({losses} pertes)")

            # Attaquant détruit
            attacker_cell.army = None

        else:
            # Égalité - les deux perdent des unités
            attacker.count = max(1, attacker.count - 1)
            defender.count = max(1, defender.count - 1)

            self.log_event("[COMBAT] Combat indecis")

            # Attaquant ne bouge pas

    def is_passable_terrain(self, cell):
        return cell.terrain != TerrainType.WATER

    def can_step_through(self, cell, moving_army, is_goal=False):
        if not self.is_passable_terrain(cell):
            return False
        if not cell.army:
            return True
        if cell.army.country != moving_army.country:
            return is_goal
        if is_goal:
            return cell.army.unit_type == moving_army.unit_type
        return False

    def get_adjacent_enemy_cells(self, from_cell, country):
        targets = set()
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = from_cell.x + dx, from_cell.y + dy
            if not (0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS):
                continue
            neighbor = self.grid[nx][ny]
            if neighbor.army and neighbor.army.country not in (country, Country.NONE):
                targets.add((nx, ny))
        return targets

    def apply_bridge_wear(self, path_cells):
        for cell in path_cells:
            if cell.terrain != TerrainType.BRIDGE:
                continue
            if cell.bridge_hp <= 0:
                cell.bridge_hp = 3
            cell.bridge_hp -= 1
            if cell.bridge_hp > 0:
                continue
            cell.terrain = TerrainType.WATER
            cell.country = Country.NONE
            cell.bridge_hp = 0
            if cell.army:
                cell.army = None
                self.log_event("[MAP] Une armee a coule avec un pont")
            self.log_event("[MAP] Un pont s'est effondre")
            self.add_animation([(cell.x, cell.y)], (120, 150, 220), 20)

    def find_path(self, from_cell, to_cell, max_range, moving_army):
        """BFS pathfinding up to max_range. Returns list excluding start."""
        start = (from_cell.x, from_cell.y)
        goal = (to_cell.x, to_cell.y)
        queue = deque([start])
        came_from = {start: None}
        dist = {start: 0}
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == goal:
                break
            if dist[(cx, cy)] >= max_range:
                continue

            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS):
                    continue
                if (nx, ny) in came_from:
                    continue
                next_cell = self.grid[nx][ny]
                is_goal = (nx, ny) == goal
                if not self.can_step_through(next_cell, moving_army, is_goal=is_goal):
                    continue
                came_from[(nx, ny)] = (cx, cy)
                dist[(nx, ny)] = dist[(cx, cy)] + 1
                queue.append((nx, ny))

        if goal not in came_from:
            return []

        path_coords = []
        cur = goal
        while cur != start:
            path_coords.append(cur)
            cur = came_from[cur]
        path_coords.reverse()
        return [self.grid[x][y] for x, y in path_coords]

    def conquer_path(self, path_cells):
        """Conquiert les cases traversées (hors eau) pendant un déplacement."""
        for cell in path_cells:
            if cell.terrain in (TerrainType.WATER,):
                continue
            if cell.country != self.current_player_country:
                cell.country = self.current_player_country

    def build_bridge_on_cell(self, cell):
        """Construit un pont sur une case d'eau adjacente à un territoire allié."""
        player = self.players[self.current_player_country]

        if cell.terrain != TerrainType.WATER:
            return False

        if cell.army:
            return False

        if player.gold < BRIDGE_COST:
            self.log_event(f"Pas assez d'or pour un pont ({player.gold}/{BRIDGE_COST})")
            return False

        adjacent_allied = False
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = cell.x + dx, cell.y + dy
            if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                neighbor = self.grid[nx][ny]
                if neighbor.country == self.current_player_country and neighbor.terrain != TerrainType.WATER:
                    adjacent_allied = True
                    break

        if not adjacent_allied:
            return False

        player.spend_gold(BRIDGE_COST)
        cell.terrain = TerrainType.BRIDGE
        cell.country = self.current_player_country
        cell.bridge_hp = 3
        self.log_event(f"[OK] Pont construit. Or: {player.gold}")
        self.add_animation([(cell.x, cell.y)], (200, 170, 110), 18)
        return True

    def compute_bridge_targets(self):
        targets = set()
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.grid[x][y]
                if cell.terrain != TerrainType.WATER or cell.army:
                    continue
                if self.build_bridge_on_cell_preview(cell):
                    targets.add((x, y))
        self.bridge_targets = targets

    def build_bridge_on_cell_preview(self, cell):
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = cell.x + dx, cell.y + dy
            if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                neighbor = self.grid[nx][ny]
                if neighbor.country == self.current_player_country and neighbor.terrain != TerrainType.WATER:
                    return True
        return False

    def reset_army_moves_for_country(self, country):
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.grid[x][y]
                if cell.army and cell.army.country == country:
                    cell.army.has_moved = False
                    cell.army.movement_left = UNIT_MOVEMENT_RANGE.get(cell.army.unit_type, MOVEMENT_RANGE)

    def get_reachable_cells(self, from_cell):
        """Retourne les cibles atteignables et attaquables depuis une armée."""
        move_targets = set()
        attack_targets = set()
        if not from_cell or not from_cell.army:
            return move_targets, attack_targets
        if from_cell.army.has_moved:
            return move_targets, attack_targets

        max_range = from_cell.army.movement_left
        engaged_targets = self.get_adjacent_enemy_cells(from_cell, self.current_player_country)
        if engaged_targets:
            attack_targets |= engaged_targets
            return move_targets, attack_targets

        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                target = self.grid[x][y]
                if target == from_cell:
                    continue
                path_cells = self.find_path(from_cell, target, max_range, from_cell.army)
                if not path_cells:
                    continue

                if target.army and target.army.country != self.current_player_country:
                    attack_targets.add((x, y))
                else:
                    move_targets.add((x, y))
        return move_targets, attack_targets

    def check_victory(self):
        """Victoire si un seul pays possède toutes les capitales."""
        owners = set()
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.grid[x][y]
                if cell.is_capital:
                    owners.add(cell.country)

        owners.discard(Country.NONE)
        if len(owners) == 1:
            winner = owners.pop()
            if self.winner_country != winner:
                self.winner_country = winner
                print(f"[WIN] {COUNTRY_NAMES[winner]} contrôle toutes les capitales !")
                self.log_event(f"[WIN] {COUNTRY_NAMES[winner]} controle toutes les capitales")

    def init_players(self):
        """Initialise les joueurs selon le mode de jeu"""
        self.players = {}

        # Crée un joueur pour chaque pays actif
        for country in [Country.RED, Country.GREEN, Country.BLUE, Country.YELLOW, Country.ORANGE]:
            player = Player(country)

            # En mode Solo, seul Rouge est humain
            if self.game_mode == "solo" and country != Country.RED:
                player.is_ai = True

            self.players[country] = player

        self.current_player_country = Country.RED
        self.turn_number = 1

        self.log_event(f"Partie demarree en mode {self.game_mode}")
        for country, player in self.players.items():
            print(f"  {player} (IA: {player.is_ai})")

    def next_turn(self):
        """Passe au tour suivant"""
        if self.winner_country:
            return

        # Liste des pays dans l'ordre
        countries = [Country.RED, Country.GREEN, Country.BLUE, Country.YELLOW, Country.ORANGE]
    
        current_index = countries.index(self.current_player_country)
        next_index = (current_index + 1) % len(countries)
        self.current_player_country = countries[next_index]
    
        # Si on revient au premier joueur, incrémente le numéro de tour
        if self.current_player_country == Country.RED:
            self.turn_number += 1
            print(f"\n=== Tour {self.turn_number} ===")
    
        # Génère l'or pour le joueur actuel
        self.generate_income()
        self.reset_army_moves_for_country(self.current_player_country)
    
        self.log_event(f"Tour de {COUNTRY_NAMES[self.current_player_country]}")
        
        # Si c'est un joueur IA, joue automatiquement
        player = self.players[self.current_player_country]
        if player.is_ai:
            self.ai.play_turn(self.current_player_country)
            self.check_victory()
            if self.winner_country:
                return
            # Passe automatiquement au tour suivant après 1 seconde
            pygame.time.wait(1000)
            self.next_turn()

    def generate_income(self):
        """Génère l'or pour le joueur actuel"""
        player = self.players[self.current_player_country]

        # Compte les capitales du joueur
        capitals = 0
        cities = 0
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.grid[x][y]
                if cell.country == self.current_player_country:
                    if cell.is_capital:
                        capitals += 1
                    if cell.is_city:
                        cities += 1

        # Revenu des capitales et villes
        capital_income = capitals * 100
        city_income = cities * CITY_INCOME
        income = capital_income + city_income

        # Entretien des armées
        upkeep = player.calculate_upkeep(self.grid)

        # Total
        net_income = income - upkeep
        player.add_gold(net_income)
        self.last_income = income
        self.last_upkeep = upkeep

        self.log_event(f"{COUNTRY_NAMES[player.country]}: +{income} -{upkeep} = {net_income} or")

    def place_capitals(self):
        self.grid[3][3].is_capital = True
        self.grid[7][8].is_capital = True
        self.grid[14][4].is_capital = True
        self.grid[4][23].is_capital = True
        self.grid[14][21].is_capital = True

    def place_test_armies(self):
        """Place quelques armées pour tester"""
        # Rouge
        self.grid[4][4].army = Army(Country.RED, UnitType.SWORDSMAN, 5)
        self.grid[5][5].army = Army(Country.RED, UnitType.CAVALRY, 3)

        # Vert
        self.grid[8][9].army = Army(Country.GREEN, UnitType.CROSSBOWMAN, 4)

        # Bleu
        self.grid[14][5].army = Army(Country.BLUE, UnitType.SWORDSMAN, 6)

        # Jaune
        self.grid[4][24].army = Army(Country.YELLOW, UnitType.CAVALRY, 2)

        # Orange
        self.grid[15][22].army = Army(Country.ORANGE, UnitType.CROSSBOWMAN, 3)

    def generate_map(self):
        # [Garde tout le code de generate_map exactement pareil]
        ile1 = [
            (2,2), (3,2), (4,2), (5,2), (6,2),
            (1,3), (2,3), (3,3), (4,3), (5,3), (6,3), (7,3),
            (1,4), (2,4), (3,4), (4,4), (5,4), (6,4), (7,4), (8,4),
            (1,5), (2,5), (3,5), (4,5), (5,5), (6,5), (7,5), (8,5), (9,5),
            (2,6), (3,6), (4,6), (5,6), (6,6), (7,6), (8,6), (9,6),
            (2,7), (3,7), (4,7), (5,7), (6,7), (7,7), (8,7), (9,7), (10,7),
            (3,8), (4,8), (5,8), (6,8), (7,8), (8,8), (9,8), (10,8),
            (3,9), (4,9), (5,9), (6,9), (7,9), (8,9), (9,9),
            (4,10), (5,10), (6,10), (7,10), (8,10),
            (5,11), (6,11), (7,11),
        ]
        rouge = [
            (2,2), (3,2), (4,2), (5,2),
            (1,3), (2,3), (3,3), (4,3), (5,3),
            (1,4), (2,4), (3,4), (4,4), (5,4),
            (1,5), (2,5), (3,5), (4,5),
            (2,6), (3,6), (4,6),
        ]
        vert = [
            (6,2), (6,3), (7,3),
            (6,4), (7,4), (8,4),
            (5,5), (6,5), (7,5), (8,5), (9,5),
            (5,6), (6,6), (7,6), (8,6), (9,6),
            (5,7), (6,7), (7,7), (8,7), (9,7), (10,7),
            (5,8), (6,8), (7,8), (8,8), (9,8), (10,8),
            (5,9), (6,9), (7,9), (8,9), (9,9),
            (5,10), (6,10), (7,10), (8,10),
            (5,11), (6,11), (7,11),
        ]
        
        ile2 = [
            (13,1), (14,1), (15,1),
            (12,2), (13,2), (14,2), (15,2), (16,2),
            (12,3), (13,3), (14,3), (15,3), (16,3), (17,3),
            (11,4), (12,4), (13,4), (14,4), (15,4), (16,4), (17,4),
            (11,5), (12,5), (13,5), (14,5), (15,5), (16,5),
            (12,6), (13,6), (14,6), (15,6), (16,6),
            (13,7), (14,7), (15,7),
            (14,8), (15,8),
        ]
        
        ile3 = [
            (2,19), (3,19), (4,19),
            (1,20), (2,20), (3,20), (4,20), (5,20),
            (1,21), (2,21), (3,21), (4,21), (5,21), (6,21),
            (2,22), (3,22), (4,22), (5,22), (6,22), (7,22),
            (2,23), (3,23), (4,23), (5,23), (6,23), (7,23),
            (3,24), (4,24), (5,24), (6,24), (7,24),
            (3,25), (4,25), (5,25), (6,25),
            (4,26), (5,26), (6,26),
            (4,27), (5,27),
        ]
        
        ile4 = [
            (14,18), (15,18), (16,18),
            (13,19), (14,19), (15,19), (16,19), (17,19),
            (12,20), (13,20), (14,20), (15,20), (16,20), (17,20), (18,20),
            (12,21), (13,21), (14,21), (15,21), (16,21), (17,21), (18,21),
            (11,22), (12,22), (13,22), (14,22), (15,22), (16,22), (17,22),
            (11,23), (12,23), (13,23), (14,23), (15,23), (16,23),
            (12,24), (13,24), (14,24), (15,24), (16,24),
            (13,25), (14,25), (15,25),
            (14,26), (15,26),
        ]
        
        ile5 = [
            (8,14), (9,14), (10,14),
            (7,15), (8,15), (9,15), (10,15), (11,15),
            (7,16), (8,16), (9,16), (10,16), (11,16),
            (8,17), (9,17), (10,17), (11,17),
            (9,18), (10,18), (11,18),
        ]
        
        self.apply_terrain(ile1, TerrainType.PLAIN)
        self.apply_terrain([(2,2), (3,2), (2,3), (3,3), (2,4), (3,4)], TerrainType.MOUNTAIN)
        self.apply_terrain([(7,5), (8,5), (7,6), (8,6), (7,7), (8,7)], TerrainType.FOREST)
        
        self.apply_terrain(ile2, TerrainType.PLAIN)
        self.apply_terrain([(14,3), (15,3), (14,4), (15,4), (14,5), (15,5)], TerrainType.MOUNTAIN)
        self.apply_terrain([(12,2), (12,3), (12,4), (11,4), (11,5)], TerrainType.FOREST)
        
        self.apply_terrain(ile3, TerrainType.PLAIN)
        self.apply_terrain([(3,22), (4,22), (3,23), (4,23), (3,24)], TerrainType.MOUNTAIN)
        self.apply_terrain([(5,20), (6,21), (6,22), (6,23), (7,23)], TerrainType.FOREST)
        
        self.apply_terrain(ile4, TerrainType.PLAIN)
        self.apply_terrain([(14,21), (15,21), (14,22), (15,22), (14,23), (15,23)], TerrainType.MOUNTAIN)
        self.apply_terrain([(12,20), (12,21), (11,22), (11,23), (12,22)], TerrainType.FOREST)
        
        self.apply_terrain(ile5, TerrainType.PLAIN)
        self.apply_terrain([(9,15), (10,15), (9,16), (10,16)], TerrainType.MOUNTAIN)
        
        self.apply_country(rouge, Country.RED)
        self.apply_country(vert, Country.GREEN)
        self.apply_country(ile2, Country.BLUE)
        self.apply_country(ile3, Country.YELLOW)
        self.apply_country(ile4, Country.ORANGE)
        self.apply_country(ile5, Country.RED)
        
        self.add_beaches()
        self.place_capitals()
        self.place_test_armies()  # NOUVEAU

    def apply_terrain(self, coords, terrain):
        for x, y in coords:
            if 0 <= x < GRID_COLS and 0 <= y < GRID_ROWS:
                self.grid[x][y].terrain = terrain
    
    def apply_country(self, coords, country):
        for x, y in coords:
            if 0 <= x < GRID_COLS and 0 <= y < GRID_ROWS:
                self.grid[x][y].country = country
    
    def add_beaches(self):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                if self.grid[x][y].terrain == TerrainType.WATER:
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                            if self.grid[nx][ny].terrain not in [TerrainType.WATER, TerrainType.BEACH]:
                                self.grid[x][y].terrain = TerrainType.BEACH
                                break
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == "menu":
                action = self.menu.handle_event(event)
                if action == "start_solo":
                    self.start_game("solo")
                elif action == "start_godgame":
                    self.start_game("godgame")
                elif action == "load":
                    print("Chargement d'une partie (pas encore implémenté)")
                elif action == "quit":
                    self.running = False

            elif self.state == "playing":
                if self.winner_country:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        print("[WIN] Partie terminée - relance une nouvelle partie depuis le menu.")
                    continue

                # Gestion UI
                ui_action = self.ui.handle_event(event, self)
                if ui_action == "end_turn":
                    self.next_turn()
                    continue
                elif ui_action == "build_city":
                    self.build_city()
                    continue
                elif ui_action == "build_bridge":
                    if not self.selected_cell or self.selected_cell.country != self.current_player_country:
                        self.log_event("Selectionne une case alliee puis choisis Construire pont")
                    else:
                        self.bridge_mode = True
                        self.compute_bridge_targets()
                        self.log_event("Mode pont: clique une case d'eau en surbrillance")
                    continue
                elif ui_action == "move_army":
                    if (
                        self.selected_cell
                        and self.selected_cell.army
                        and self.selected_cell.army.country == self.current_player_country
                    ):
                        self.selected_army_cell = self.selected_cell
                        self.bridge_mode = False
                        self.bridge_targets.clear()
                        self.move_targets, self.attack_targets = self.get_reachable_cells(self.selected_army_cell)
                        self.log_event(f"[MOVE] Choisis la destination de {UNIT_NAMES[self.selected_cell.army.unit_type]}")
                    continue
                elif ui_action and ui_action[0] == "recruit":
                    unit_type = ui_action[1]
                    self.recruit_unit(unit_type)
                    continue
                
                # Clic sur la map
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    cell_x = x // CELL_SIZE
                    cell_y = y // CELL_SIZE

                    if 0 <= cell_x < GRID_COLS and 0 <= cell_y < GRID_ROWS:
                        if (cell_x, cell_y) not in self.visibility:
                            self.log_event("Zone non visible (fog of war)")
                            continue
                        clicked_cell = self.grid[cell_x][cell_y]

                        if self.bridge_mode:
                            built = self.build_bridge_on_cell(clicked_cell)
                            if not built:
                                self.log_event("Pont impossible ici (case d'eau adjacente requise)")
                            self.bridge_mode = False
                            self.bridge_targets.clear()
                            continue

                        # Si on a déjà une armée sélectionnée pour le mouvement
                        if self.selected_army_cell:
                            # Tente de déplacer vers la case cliquée
                            self.move_army(self.selected_army_cell, clicked_cell)
                            self.selected_army_cell = None
                            self.move_targets.clear()
                            self.attack_targets.clear()

                        # Sinon, sélection normale
                        else:
                            if self.selected_cell:
                                self.selected_cell.is_selected = False

                            self.selected_cell = clicked_cell
                            self.selected_cell.is_selected = True
                            self.move_targets.clear()
                            self.attack_targets.clear()

                            self.log_event(f"Case ({cell_x},{cell_y}) {self.selected_cell.terrain.name}")
                elif event.type == pygame.MOUSEMOTION:
                    x, y = event.pos
                    cell_x = x // CELL_SIZE
                    cell_y = y // CELL_SIZE
                    if 0 <= cell_x < GRID_COLS and 0 <= cell_y < GRID_ROWS:
                        self.hovered_cell = self.grid[cell_x][cell_y]
                    else:
                        self.hovered_cell = None

    def compute_visibility(self):
        """Fog of war based on current player's units and owned territory."""
        visible = set()
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.grid[x][y]
                is_source = (
                    cell.country == self.current_player_country
                    or (cell.army and cell.army.country == self.current_player_country)
                )
                if not is_source:
                    continue
                for dx in range(-FOG_RADIUS, FOG_RADIUS + 1):
                    for dy in range(-FOG_RADIUS, FOG_RADIUS + 1):
                        if abs(dx) + abs(dy) > FOG_RADIUS:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                            visible.add((nx, ny))
                            self.grid[nx][ny].discovered_by.add(self.current_player_country)
        self.visibility = visible

    def update(self):
        for animation in self.animations:
            animation["ttl"] -= 1
        self.animations = [a for a in self.animations if a["ttl"] > 0]
    
    def draw(self):
        if self.state == "menu":
            self.menu.draw()
        
        elif self.state == "playing":
            self.screen.fill((0, 0, 0))
            self.compute_visibility()
            
            for x in range(GRID_COLS):
                for y in range(GRID_ROWS):
                    self.grid[x][y].draw(self.screen, self.assets)

            # Highlights de déplacement / attaque
            for x, y in self.move_targets:
                highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                highlight.fill((52, 152, 219, 70))
                self.screen.blit(highlight, (x * CELL_SIZE, y * CELL_SIZE))
            for x, y in self.attack_targets:
                highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                highlight.fill((231, 76, 60, 85))
                self.screen.blit(highlight, (x * CELL_SIZE, y * CELL_SIZE))
            for x, y in self.bridge_targets:
                highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                highlight.fill((200, 170, 110, 95))
                self.screen.blit(highlight, (x * CELL_SIZE, y * CELL_SIZE))

            # Fog of war
            for x in range(GRID_COLS):
                for y in range(GRID_ROWS):
                    cell = self.grid[x][y]
                    if (x, y) in self.visibility:
                        continue
                    fog_tile = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    if self.current_player_country in cell.discovered_by:
                        fog_tile.fill((10, 12, 16, 200))
                    else:
                        fog_tile.fill((0, 0, 0, 250))
                    self.screen.blit(fog_tile, (x * CELL_SIZE, y * CELL_SIZE))

            for animation in self.animations:
                alpha = max(20, int(180 * (animation["ttl"] / animation["max_ttl"])))
                for x, y in animation["cells"]:
                    pulse = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    pulse.fill((*animation["color"], alpha))
                    self.screen.blit(pulse, (x * CELL_SIZE, y * CELL_SIZE))
            
            self.ui.draw(self)
            self.draw_tooltip()
            
            pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

    def log_event(self, message):
        print(message)
        self.event_log.append(message)
        if len(self.event_log) > 8:
            self.event_log.pop(0)

    def add_animation(self, cells, color, ttl):
        self.animations.append({
            "cells": cells,
            "color": color,
            "ttl": ttl,
            "max_ttl": ttl,
        })

    def draw_tooltip(self):
        if not self.hovered_cell:
            return
        x, y = pygame.mouse.get_pos()
        if x >= GRID_COLS * CELL_SIZE:
            return
        if (self.hovered_cell.x, self.hovered_cell.y) not in self.visibility:
            return

        lines = [
            f"({self.hovered_cell.x},{self.hovered_cell.y})",
            f"Terrain: {TERRAIN_FULL_NAMES[self.hovered_cell.terrain]}",
            f"Pays: {COUNTRY_NAMES[self.hovered_cell.country]}",
        ]
        if self.hovered_cell.terrain == TerrainType.BRIDGE:
            lines.append(f"Pont HP: {self.hovered_cell.bridge_hp}")
        if self.hovered_cell.army:
            lines.append(
                f"{UNIT_NAMES[self.hovered_cell.army.unit_type]} x{self.hovered_cell.army.count} PM:{self.hovered_cell.army.movement_left}"
            )

        font = pygame.font.Font(None, 18)
        width = max(font.size(line)[0] for line in lines) + 12
        height = len(lines) * 18 + 10
        tx = min(x + 12, GRID_COLS * CELL_SIZE - width - 4)
        ty = min(y + 12, WINDOW_HEIGHT - height - 4)
        bg = pygame.Surface((width, height), pygame.SRCALPHA)
        bg.fill((20, 20, 24, 230))
        self.screen.blit(bg, (tx, ty))
        for idx, line in enumerate(lines):
            text = font.render(line, True, (230, 230, 230))
            self.screen.blit(text, (tx + 6, ty + 5 + idx * 18))

if __name__ == "__main__":
    game = Game()
    game.run()