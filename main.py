import math
import heapq
import pygame
import sys
from constants import *
from cell import Cell, draw_army_at
from ui import UI
from menu import Menu
from army import Army
from player import Player
from ai import AI
from asset_loader import AssetLoader
from map_generator import MapGenerator
from save_game import save_game, load_game, SAVE_PATH
from audio import AudioManager
from tutorial import Tutorial
from pause_menu import PauseMenu
from settings import load_settings, AI_SPEED_DELAYS_MS, DIFFICULTY_CONFIG
from fx import Effects, draw_end_recap

DEFEAT_LOOT_RATIO = 0.25
SOLO_HUMAN_COUNTRY = Country.RED


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("The World Is Ours")
        self.clock = pygame.time.Clock()
        self.running = True
        self.settings = load_settings()
        self.assets = AssetLoader("assets")
        self.audio = AudioManager(volume=self.settings["volume"])
        self.tutorial = Tutorial()
        self.pause_menu = PauseMenu(self.screen)
        self.fx = Effects()
        self.map_seed = None
        self.last_aggressor = {}
        
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
        self.ranged_targets = set()
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
        self.defeated_countries = set()
        self.ranged_mode = False
        self.game_over_message = ""
        self.player_defeated = False
        self.preview_path_cells = []
        self.move_costs = {}
        self.occupation_tracker = {}
        self.ai_turn_pending = False
        self.ai_turn_resume_at = 0
        self.disembark_targets = set()
        self.embark_targets = set()
        self.gold_looted = {}
        self.audio.play_music("menu")

    def start_game(self, mode):
        """Démarre une nouvelle partie"""
        self.settings = load_settings()
        self.audio.set_volume(self.settings["volume"])
        self.difficulty_cfg = DIFFICULTY_CONFIG.get(
            self.settings.get("difficulty", "normal"), DIFFICULTY_CONFIG["normal"]
        )
        self.game_mode = mode
        self.state = "playing"
        self.pause_menu.close()
        
        # Initialise le jeu
        self.grid = [[Cell(x, y) for y in range(GRID_ROWS)] for x in range(GRID_COLS)]
        self.selected_cell = None
        self.selected_army_cell = None
        self.move_targets.clear()
        self.attack_targets.clear()
        self.ranged_targets.clear()
        self.winner_country = None
        self.visibility.clear()
        self.event_log.clear()
        self.animations.clear()
        self.bridge_mode = False
        self.bridge_targets.clear()
        self.defeated_countries.clear()
        self.ranged_mode = False
        self.game_over_message = ""
        self.player_defeated = False
        self.preview_path_cells = []
        self.move_costs = {}
        self.occupation_tracker = {}
        self.ai_turn_pending = False
        self.ai_turn_resume_at = 0
        self.last_aggressor = {}
        self.disembark_targets = set()
        self.embark_targets = set()
        self.gold_looted = {}
        self.fx.clear()
        self.ui = UI(self.screen)

        self.ai = AI(self)
        MapGenerator().generate(self)
        self.init_players()
        self.place_starting_armies()
        self.tutorial.start()
        self.audio.play_music("game")
        self.fx.show_banner(f"Tour de {COUNTRY_NAMES[self.current_player_country]}")
        self.log_event("Nouvelle carte générée")
        self.select_next_idle_army()
    
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
        if cell.last_recruit_turn == self.turn_number:
            print("Cette ville a deja recrute ce tour")
            return

        cost = player.unit_cost(unit_type)
        if not player.can_afford(unit_type):
            print(f"Pas assez d'or ! ({player.gold}/{cost})")
            return

        if cell.army and cell.army.unit_type != unit_type:
            self.log_event("Case occupee par un autre type d'unite")
            return
        if cell.army and cell.army.count >= MAX_UNITS_PER_ARMY:
            self.log_event(f"Cap atteint ({MAX_UNITS_PER_ARMY})")
            return

        if not player.spend_gold(cost):
            return

        self.audio.play("recruit")
        if cell.army:
            cell.army.count += 1
        else:
            cell.army = Army(self.current_player_country, unit_type, 1)
            cell.army.refresh_movement(player)
        cell.last_recruit_turn = self.turn_number

        self.log_event(f"{UNIT_NAMES[unit_type]} recruté. Or: {player.gold}")
    
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

        # Vérifie l'or
        if player.gold < CITY_COST:
            print(f"Pas assez d'or pour construire une ville ! ({player.gold}/{CITY_COST})")
            return

        # Construit
        player.spend_gold(CITY_COST)
        cell.is_city = True
        cell.city_owner = self.current_player_country
        self.audio.play("build")
        self.log_event(f"Ville construite. Or: {player.gold}")

    def move_army(self, from_cell, to_cell):
        """Déplace une armée d'une case à une autre"""
        if not from_cell.army:
            print("Pas d'armée à déplacer")
            return

        army = from_cell.army
        army.is_fortified = False

        # Vérifications
        if army.country != self.current_player_country:
            print("Ce n'est pas votre armée")
            return
        if army.has_moved:
            self.log_event("Cette armée a déjà bougé ce tour")
            return
        if army.movement_left <= 0:
            self.log_event("Cette armée n'a plus de mouvement")
            return

        if army.embarked:
            if to_cell.terrain not in NAVAL_TERRAINS:
                self.log_event("Un navire doit débarquer pour aller à terre")
                return
        elif to_cell.terrain == TerrainType.WATER:
            self.log_event("Impossible de se déplacer sur l'eau")
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
        move_cost = self.path_move_cost(path_cells, army)

        if self.is_enemy_urban(to_cell, army.country) and not army.embarked:
            self.ensure_city_garrison(to_cell)

        # Si case ennemie avec armée → COMBAT
        if to_cell.army and to_cell.army.country != self.current_player_country:
            if army.embarked and not to_cell.army.embarked:
                self.log_event("Débarque d'abord pour attaquer à terre")
                return
            if not army.embarked and to_cell.army.embarked:
                self.log_event("Impossible d'aborder un navire à pied")
                return
            result = self.battle(from_cell, to_cell)
            self.audio.play("battle")
            if result:
                self.fx.float_text(to_cell.x, to_cell.y, f"-{result['losses']}", (231, 76, 60))
                self.add_animation([(to_cell.x, to_cell.y)], (231, 76, 60), 16)
            if to_cell.army and to_cell.army.country == self.current_player_country:
                to_cell.army.movement_left = max(0, to_cell.army.movement_left - move_cost)
                to_cell.army.has_moved = to_cell.army.movement_left <= 0
                self.apply_bridge_wear(path_cells)
            elif from_cell.army and from_cell.army.country == self.current_player_country:
                from_cell.army.movement_left = 0
                from_cell.army.has_moved = True
            self.evaluate_occupation_pressure()
            self.check_victory()
            return

        if to_cell.army:
            if to_cell.army.unit_type != army.unit_type:
                self.log_event("Impossible de fusionner des unites differentes")
                return
            if to_cell.army.count >= MAX_UNITS_PER_ARMY:
                self.log_event(f"Case pleine (max {MAX_UNITS_PER_ARMY})")
                return

        if not army.embarked:
            self.conquer_path(path_cells)

        if (
            not army.embarked
            and to_cell.country != Country.NONE
            and to_cell.country != self.current_player_country
        ):
            if to_cell.is_city or to_cell.is_capital:
                self.record_aggression(self.current_player_country, to_cell.country)
                kind = "Capitale" if to_cell.is_capital else "Ville"
                self.log_event(f"{kind} prise")
                to_cell.country = self.current_player_country
                to_cell.garrison_ready = True
            else:
                self.record_aggression(self.current_player_country, to_cell.country)
                self.log_event(f"Conquête de {COUNTRY_NAMES[to_cell.country]}")
                to_cell.country = self.current_player_country

        if to_cell.army:
            capacity = MAX_UNITS_PER_ARMY - to_cell.army.count
            transfer = min(capacity, army.count)
            to_cell.army.count += transfer
            army.count -= transfer
            to_cell.army.movement_left = max(0, to_cell.army.movement_left - move_cost)
            to_cell.army.has_moved = to_cell.army.movement_left <= 0
            if army.count <= 0:
                from_cell.army = None
                self.log_event(f"Armées fusionnées ({to_cell.army.count})")
            else:
                army.has_moved = True
                army.movement_left = 0
                self.log_event(f"Fusion partielle ({to_cell.army.count}/{MAX_UNITS_PER_ARMY})")
        else:
            # Déplacement simple
            to_cell.army = army
            to_cell.army.movement_left = max(0, to_cell.army.movement_left - move_cost)
            to_cell.army.has_moved = to_cell.army.movement_left <= 0
            from_cell.army = None
            self.log_event("Déplacement effectué")
        self.audio.play("move")
        self.add_animation([(from_cell.x, from_cell.y), (to_cell.x, to_cell.y)], (52, 152, 219), 14)
        self.apply_bridge_wear(path_cells)

        self.update_defeat_states()
        self.evaluate_occupation_pressure()
        self.check_victory()

    def battle(self, attacker_cell, defender_cell):
        """Gère un combat entre deux armées"""
        attacker = attacker_cell.army
        defender = defender_cell.army
        self.record_aggression(attacker.country, defender.country)

        self.log_event(f"{COUNTRY_NAMES[attacker.country]} attaque {COUNTRY_NAMES[defender.country]}")

        # Système RPS (Pierre-Papier-Ciseaux)
        # Spadassin > Arbalétrier > Cavalerie > Spadassin
        attacker_type = attacker.unit_type
        defender_type = defender.unit_type

        attacker_advantage = self.combat_advantage(attacker_type, defender_type)
        if attacker_type == UnitType.CATAPULT and (defender_cell.is_city or defender_cell.is_capital):
            attacker_advantage += 2

        attacker_player = self.players.get(attacker.country)
        defender_player = self.players.get(defender.country)
        attack_bonus = 0
        if attacker_player and attacker_type == UnitType.SWORDSMAN:
            attack_bonus += attacker_player.swordsman_attack_bonus

        terrain_bonus = TERRAIN_DEFENSE_BONUS[defender_cell.terrain]
        if defender_cell.terrain == TerrainType.FOREST and defender_player:
            terrain_bonus += defender_player.forest_defense_bonus
        if defender_cell.is_capital:
            terrain_bonus += CAPITAL_WALL_BONUS
        elif defender_cell.is_city:
            terrain_bonus += CITY_WALL_BONUS
        if defender.is_fortified:
            terrain_bonus += FORTIFY_DEFENSE_BONUS
            defender.is_fortified = False

        attacker_power = attacker.count * (
            UNIT_STATS[attacker_type]["attack"] + attacker_advantage + attack_bonus
        )
        defender_power = defender.count * (UNIT_STATS[defender_type]["defense"] + terrain_bonus)

        print(f"  Force attaquant: {attacker_power} (avantage RPS: {attacker_advantage:+d})")
        print(f"  Force défenseur: {defender_power} (bonus terrain: +{terrain_bonus})")

        if attacker_power > defender_power:
            losses = max(1, defender.count // 2)
            attacker.count = max(1, attacker.count - losses)
            self.log_event(f"{COUNTRY_NAMES[attacker.country]} gagne ({losses} pertes)")
            defender_cell.country = attacker.country
            defender_cell.garrison_ready = True
            defender_cell.army = attacker
            attacker_cell.army = None
            return {"losses": losses, "winner": "attacker"}
        if defender_power > attacker_power:
            losses = max(1, attacker.count // 2)
            defender.count = max(1, defender.count - losses)
            self.log_event(f"{COUNTRY_NAMES[defender.country]} défend ({losses} pertes)")
            attacker_cell.army = None
            return {"losses": losses, "winner": "defender"}
        attacker.count = max(1, attacker.count - 1)
        defender.count = max(1, defender.count - 1)
        self.log_event("Combat indécis")
        return {"losses": 1, "winner": "draw"}

    def combat_advantage(self, attacker_type, defender_type):
        beats = {
            UnitType.SWORDSMAN: (UnitType.CROSSBOWMAN, UnitType.SPEARMAN),
            UnitType.CROSSBOWMAN: (UnitType.CAVALRY,),
            UnitType.CAVALRY: (UnitType.SWORDSMAN,),
            UnitType.SPEARMAN: (UnitType.CAVALRY,),
        }
        if defender_type in beats.get(attacker_type, ()):
            return 1
        if attacker_type in beats.get(defender_type, ()):
            return -1
        return 0

    def is_enemy_urban(self, cell, country):
        if not cell or not (cell.is_city or cell.is_capital):
            return False
        return cell.country not in (country, Country.NONE)

    def ensure_city_garrison(self, cell):
        if not cell or cell.army:
            return
        if not (cell.is_city or cell.is_capital) or cell.country == Country.NONE:
            return
        if not getattr(cell, "garrison_ready", True):
            return
        count = CAPITAL_GARRISON_COUNT if cell.is_capital else CITY_GARRISON_COUNT
        cell.army = Army(cell.country, UnitType.SPEARMAN, count)
        cell.army.movement_left = 0
        cell.army.has_moved = True
        cell.garrison_ready = False
        self.log_event(f"Garnison : {count} lanciers sortent des murs")

    def is_passable_terrain(self, cell, moving_army=None):
        if moving_army and moving_army.embarked:
            return cell.terrain in NAVAL_TERRAINS
        return cell.terrain != TerrainType.WATER

    def can_step_through(self, cell, moving_army, is_goal=False):
        if not self.is_passable_terrain(cell, moving_army):
            return False
        if not cell.army:
            if self.is_enemy_urban(cell, moving_army.country):
                return is_goal and not moving_army.embarked
            return True
        if cell.army.country != moving_army.country:
            if moving_army.embarked:
                return is_goal and cell.army.embarked
            return is_goal and not cell.army.embarked
        if is_goal:
            return cell.army.unit_type == moving_army.unit_type and cell.army.embarked == moving_army.embarked
        return False

    def get_adjacent_enemy_cells(self, from_cell, country):
        targets = set()
        army = from_cell.army
        embarked = bool(army and army.embarked)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = from_cell.x + dx, from_cell.y + dy
            if not (0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS):
                continue
            neighbor = self.grid[nx][ny]
            if neighbor.army and neighbor.army.country not in (country, Country.NONE):
                if embarked:
                    if neighbor.army.embarked:
                        targets.add((nx, ny))
                elif not neighbor.army.embarked:
                    targets.add((nx, ny))
                continue
            if not embarked and self.is_enemy_urban(neighbor, country):
                targets.add((nx, ny))
        return targets

    def get_ranged_targets(self, from_cell):
        targets = set()
        if not from_cell or not from_cell.army:
            return targets
        army = from_cell.army
        if army.unit_type not in UNIT_RANGED_RANGE:
            return targets
        if army.movement_left <= 0:
            return targets
        player = self.players[self.current_player_country]
        max_range = UNIT_RANGED_RANGE[army.unit_type] + player.ranged_range_bonus
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                if (x, y) not in self.visibility:
                    continue
                cell = self.grid[x][y]
                distance = abs(from_cell.x - x) + abs(from_cell.y - y)
                if not (1 <= distance <= max_range):
                    continue
                if cell.army and cell.army.country not in (self.current_player_country, Country.NONE):
                    targets.add((x, y))
                elif army.unit_type == UnitType.CATAPULT and self.is_enemy_urban(cell, self.current_player_country):
                    targets.add((x, y))
        return targets

    def ranged_attack(self, attacker_cell, target_cell):
        if not attacker_cell.army or attacker_cell.army.unit_type not in UNIT_RANGED_RANGE:
            return
        attacker = attacker_cell.army
        if attacker.movement_left <= 0:
            self.log_event("Plus de mouvement pour tirer")
            return
        if attacker.unit_type == UnitType.CATAPULT and self.is_enemy_urban(target_cell, attacker.country):
            self.ensure_city_garrison(target_cell)
        if not target_cell.army or target_cell.army.country == self.current_player_country:
            self.log_event("Cible invalide")
            return

        self.record_aggression(self.current_player_country, target_cell.army.country)
        defender = target_cell.army
        player = self.players[self.current_player_country]
        damage = max(
            1,
            RANGED_BASE_DAMAGE
            + UNIT_STATS[attacker.unit_type]["attack"]
            + player.ranged_damage_bonus
            - UNIT_STATS[defender.unit_type]["defense"] // 2
        )
        if attacker.unit_type == UnitType.CATAPULT:
            damage += 2
            if target_cell.is_city or target_cell.is_capital:
                damage += 2
        if defender.is_fortified:
            damage = max(1, damage - 1)
            defender.is_fortified = False

        defender.count -= damage
        attacker.movement_left = 0
        attacker.has_moved = True
        attacker.is_fortified = False
        self.log_event(f"Tir : {damage} dégâts")
        self.audio.play("ranged")
        self.add_animation([(target_cell.x, target_cell.y)], (170, 110, 220), 18)

        if defender.count <= 0:
            target_cell.army = None
            self.log_event("Armée ennemie détruite")
        self.update_defeat_states()
        self.evaluate_occupation_pressure()
        self.check_victory()

    def fortify_selected_army(self):
        if not self.selected_cell or not self.selected_cell.army:
            self.log_event("Aucune armee selectionnee")
            return
        army = self.selected_cell.army
        if army.country != self.current_player_country:
            self.log_event("Ce n'est pas votre armee")
            return
        if army.movement_left <= 0:
            self.log_event("Armee sans PM")
            return
        army.is_fortified = True
        army.movement_left = 0
        army.has_moved = True
        self.log_event("Armée fortifiée")
        self.add_animation([(self.selected_cell.x, self.selected_cell.y)], (120, 170, 120), 16)

    def _neighbors(self, cell):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cell.x + dx, cell.y + dy
            if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                yield self.grid[nx][ny]

    def can_embark_from(self, cell):
        if not cell.army or cell.army.embarked or cell.army.movement_left <= 0:
            return False
        if self.get_adjacent_enemy_cells(cell, cell.army.country):
            return False
        return any(
            neighbor.terrain == TerrainType.WATER and not neighbor.army
            for neighbor in self._neighbors(cell)
        )

    def get_embark_targets(self, from_cell):
        targets = set()
        if not self.can_embark_from(from_cell):
            return targets
        for neighbor in self._neighbors(from_cell):
            if neighbor.terrain != TerrainType.WATER or neighbor.army:
                continue
            targets.add((neighbor.x, neighbor.y))
        return targets

    def embark_army(self, from_cell, to_cell):
        if not from_cell.army or from_cell.army.embarked:
            return False
        player = self.players[self.current_player_country]
        cost = player.embark_cost()
        if player.gold < cost:
            self.log_event(f"Pas assez d'or pour embarquer ({player.gold}/{cost})")
            return False
        if (to_cell.x, to_cell.y) not in self.get_embark_targets(from_cell):
            self.log_event("Embarquement impossible ici")
            return False
        if not player.spend_gold(cost):
            return False
        army = from_cell.army
        army.embarked = True
        army.is_fortified = False
        army.movement_left = 0
        army.has_moved = True
        if from_cell is not to_cell:
            to_cell.army = army
            from_cell.army = None
        self.audio.play("embark")
        self.log_event(f"Embarquement. Or: {player.gold}")
        self.add_animation([(to_cell.x, to_cell.y)], (80, 140, 200), 16)
        return True

    def get_disembark_targets(self, from_cell):
        targets = set()
        if not from_cell.army or not from_cell.army.embarked or from_cell.army.movement_left <= 0:
            return targets
        army = from_cell.army
        if from_cell.terrain == TerrainType.BEACH:
            targets.add((from_cell.x, from_cell.y))
        for neighbor in self._neighbors(from_cell):
            if neighbor.terrain not in DISEMBARK_TERRAINS:
                continue
            if neighbor.army:
                if neighbor.army.country != army.country:
                    if not neighbor.army.embarked:
                        targets.add((neighbor.x, neighbor.y))
                elif (
                    neighbor.army.unit_type == army.unit_type
                    and not neighbor.army.embarked
                    and neighbor.army.count < MAX_UNITS_PER_ARMY
                ):
                    targets.add((neighbor.x, neighbor.y))
            else:
                targets.add((neighbor.x, neighbor.y))
        return targets

    def disembark_army(self, from_cell, to_cell):
        if not from_cell.army or not from_cell.army.embarked:
            return False
        if (to_cell.x, to_cell.y) not in self.get_disembark_targets(from_cell):
            self.log_event("Débarquement impossible ici")
            return False
        army = from_cell.army
        if from_cell is to_cell:
            army.embarked = False
            army.movement_left = 0
            army.has_moved = True
            self.log_event("Débarquement sur la plage")
            self.add_animation([(to_cell.x, to_cell.y)], (80, 160, 90), 16)
            return True
        army.embarked = False
        self.move_army(from_cell, to_cell)
        landed = to_cell.army if to_cell.army and to_cell.army.country == self.current_player_country else None
        if landed:
            landed.embarked = False
            landed.movement_left = 0
            landed.has_moved = True
        self.log_event("Débarquement")
        self.add_animation([(to_cell.x, to_cell.y)], (80, 160, 90), 16)
        return True

    def clear_order_modes(self):
        self.selected_army_cell = None
        self.move_targets.clear()
        self.attack_targets.clear()
        self.ranged_targets.clear()
        self.disembark_targets.clear()
        self.embark_targets.clear()
        self.bridge_mode = False
        self.bridge_targets.clear()
        self.ranged_mode = False
        self.preview_path_cells.clear()
        self.move_costs = {}

    def select_army_for_orders(self, cell):
        self.selected_army_cell = cell
        self.bridge_mode = False
        self.bridge_targets.clear()
        self.ranged_mode = False
        self.move_targets, self.attack_targets = self.get_reachable_cells(cell)
        self.disembark_targets = self.get_disembark_targets(cell)
        self.embark_targets = self.get_embark_targets(cell)
        if cell.army and cell.army.unit_type in UNIT_RANGED_RANGE:
            self.ranged_targets = self.get_ranged_targets(cell)
        else:
            self.ranged_targets.clear()

    def request_move(self, from_cell, to_cell, animate=None):
        if not from_cell or not from_cell.army:
            return
        if animate is None:
            animate = self.is_human_turn()
        dest = (to_cell.x, to_cell.y)

        def play(path, action):
            def wrapped():
                action()
                if animate:
                    self.maybe_advance_after_orders()

            if animate:
                self.fx.start_walk(from_cell, path, from_cell.army, wrapped)
            else:
                wrapped()

        if dest in self.get_embark_targets(from_cell) and not from_cell.army.embarked:
            path = [] if from_cell is to_cell else [to_cell]
            play(path, lambda: self.embark_army(from_cell, to_cell))
            return
        if from_cell.army.embarked and dest in self.get_disembark_targets(from_cell):
            path = [] if from_cell is to_cell else [to_cell]
            play(path, lambda: self.disembark_army(from_cell, to_cell))
            return
        path_cells = self.find_path(from_cell, to_cell, from_cell.army.movement_left, from_cell.army)
        if not path_cells:
            self.log_event("Aucun chemin valide vers cette case")
            return
        play(path_cells, lambda: self.move_army(from_cell, to_cell))


    def apply_bridge_wear(self, path_cells):
        if not path_cells:
            return
        last_index = len(path_cells) - 1
        for idx, cell in enumerate(path_cells):
            if cell.terrain != TerrainType.BRIDGE:
                continue
            # Bridge only degrades once an army leaves the tile.
            if idx == last_index:
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
                self.log_event("Une armée a coulé avec un pont")
            self.log_event("Un pont s'est effondré")
            self.add_animation([(cell.x, cell.y)], (120, 150, 220), 20)
            self.update_defeat_states()

    def terrain_move_cost(self, cell, moving_army):
        """PM spent to enter a tile. Ships always pay 1."""
        if moving_army and moving_army.embarked:
            return 1
        return TERRAIN_MOVE_COST.get(cell.terrain, 1)

    def path_move_cost(self, path_cells, moving_army):
        return sum(self.terrain_move_cost(cell, moving_army) for cell in path_cells)

    def find_path(self, from_cell, to_cell, max_range, moving_army):
        """Dijkstra: cost is spent entering each tile. Returns list excluding start."""
        start = (from_cell.x, from_cell.y)
        goal = (to_cell.x, to_cell.y)
        if start == goal:
            return []
        dist = {start: 0}
        came_from = {start: None}
        heap = [(0, start)]
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        while heap:
            cost, (cx, cy) = heapq.heappop(heap)
            if cost > dist.get((cx, cy), 10**9):
                continue
            if (cx, cy) == goal:
                break
            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS):
                    continue
                next_cell = self.grid[nx][ny]
                is_goal = (nx, ny) == goal
                if not self.can_step_through(next_cell, moving_army, is_goal=is_goal):
                    continue
                nd = cost + self.terrain_move_cost(next_cell, moving_army)
                if nd > max_range:
                    continue
                if nd < dist.get((nx, ny), 10**9):
                    dist[(nx, ny)] = nd
                    came_from[(nx, ny)] = (cx, cy)
                    heapq.heappush(heap, (nd, (nx, ny)))

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
        """Conquiert les cases traversées (hors eau et hors villes)."""
        for cell in path_cells:
            if cell.terrain in (TerrainType.WATER,):
                continue
            if cell.is_city or cell.is_capital:
                continue
            if cell.country != self.current_player_country:
                cell.country = self.current_player_country

    def build_bridge_on_cell(self, cell):
        """Construit un pont uniquement sur un détroit (eau entre deux terres)."""
        player = self.players[self.current_player_country]
        if not self.is_valid_bridge_site(cell):
            return False

        bridge_cost = player.bridge_cost()
        if player.gold < bridge_cost:
            self.log_event(f"Pas assez d'or pour un pont ({player.gold}/{bridge_cost})")
            return False

        player.spend_gold(bridge_cost)
        cell.terrain = TerrainType.BRIDGE
        cell.country = self.current_player_country
        cell.bridge_hp = 3 + player.bridge_hp_bonus
        self.log_event(f"Pont construit. Or: {player.gold}")
        self.add_animation([(cell.x, cell.y)], (200, 170, 110), 18)
        return True

    def compute_bridge_targets(self):
        targets = set()
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                if self.is_valid_bridge_site(self.grid[x][y]):
                    targets.add((x, y))
        self.bridge_targets = targets

    def _neighbor_at(self, cell, dx, dy):
        nx, ny = cell.x + dx, cell.y + dy
        if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
            return self.grid[nx][ny]
        return None

    def is_valid_bridge_site(self, cell):
        if not cell or cell.terrain != TerrainType.WATER or cell.army:
            return False
        north = self._neighbor_at(cell, 0, -1)
        south = self._neighbor_at(cell, 0, 1)
        west = self._neighbor_at(cell, -1, 0)
        east = self._neighbor_at(cell, 1, 0)

        def is_shore(tile):
            return tile is not None and tile.terrain in SHORE_TERRAINS

        crossing = (is_shore(north) and is_shore(south)) or (is_shore(west) and is_shore(east))
        if not crossing:
            return False
        return any(
            neighbor.country == self.current_player_country and neighbor.terrain in SHORE_TERRAINS
            for neighbor in self._neighbors(cell)
        )

    def has_adjacent_bridge_site(self, cell):
        if not cell:
            return False
        return any(self.is_valid_bridge_site(neighbor) for neighbor in self._neighbors(cell))

    def reset_army_moves_for_country(self, country):
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.grid[x][y]
                if cell.army and cell.army.country == country:
                    cell.army.refresh_movement(self.players.get(country))

    def get_reachable_cells(self, from_cell):
        """Retourne les cibles atteignables et attaquables depuis une armée."""
        move_targets = set()
        attack_targets = set()
        costs = {}
        if not from_cell or not from_cell.army:
            self.move_costs = costs
            return move_targets, attack_targets
        if from_cell.army.has_moved:
            self.move_costs = costs
            return move_targets, attack_targets

        max_range = from_cell.army.movement_left
        engaged_targets = self.get_adjacent_enemy_cells(from_cell, self.current_player_country)
        if engaged_targets:
            attack_targets |= engaged_targets
            for pos in engaged_targets:
                costs[pos] = 1
            self.move_costs = costs
            return move_targets, attack_targets

        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                target = self.grid[x][y]
                if target == from_cell:
                    continue
                path_cells = self.find_path(from_cell, target, max_range, from_cell.army)
                if not path_cells:
                    continue
                costs[(x, y)] = self.path_move_cost(path_cells, from_cell.army)
                if (target.army and target.army.country != self.current_player_country) or self.is_enemy_urban(
                    target, self.current_player_country
                ):
                    attack_targets.add((x, y))
                else:
                    move_targets.add((x, y))
        self.move_costs = costs
        return move_targets, attack_targets

    def check_victory(self):
        """Victoire si un seul pays possède toutes les capitales."""
        self.update_defeat_states()

        alive = [c for c in [Country.RED, Country.GREEN, Country.BLUE, Country.YELLOW, Country.ORANGE] if c not in self.defeated_countries]
        if len(alive) == 1 and self.winner_country != alive[0]:
            self.winner_country = alive[0]
            self.game_over_message = f"Victoire: {COUNTRY_NAMES[alive[0]]} (dernier royaume)"
            self.log_event(f"{COUNTRY_NAMES[alive[0]]} est le dernier royaume debout")
            self.audio.play("victory")
            return

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
                self.game_over_message = f"Victoire: {COUNTRY_NAMES[winner]} (toutes les capitales)"
                print(f"{COUNTRY_NAMES[winner]} contrôle toutes les capitales !")
                self.log_event(f"{COUNTRY_NAMES[winner]} controle toutes les capitales")
                self.audio.play("victory")

    def country_has_anything(self, country):
        has_army = False
        has_urban = False
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.grid[x][y]
                if cell.country == country:
                    if cell.is_city or cell.is_capital:
                        has_urban = True
                if cell.army and cell.army.country == country:
                    has_army = True
                if has_urban or has_army:
                    return True
        return has_urban or has_army

    def record_aggression(self, attacker, defender):
        if attacker != Country.NONE and defender != Country.NONE and attacker != defender:
            self.last_aggressor[defender] = attacker

    def infer_conqueror(self, loser):
        aggressor = self.last_aggressor.get(loser)
        if (
            aggressor
            and aggressor != loser
            and aggressor not in self.defeated_countries
        ):
            return aggressor

        border_counts = {}
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.grid[x][y]
                if cell.country != loser:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS):
                        continue
                    neighbor = self.grid[nx][ny]
                    if (
                        neighbor.country != loser
                        and neighbor.country != Country.NONE
                        and neighbor.country not in self.defeated_countries
                    ):
                        border_counts[neighbor.country] = border_counts.get(neighbor.country, 0) + 1
        if border_counts:
            return max(border_counts, key=border_counts.get)

        for country in [Country.RED, Country.GREEN, Country.BLUE, Country.YELLOW, Country.ORANGE]:
            if country != loser and country not in self.defeated_countries:
                return country
        return Country.NONE

    def eliminate_country(self, loser, conqueror=None):
        if loser in self.defeated_countries:
            return

        conqueror = conqueror or self.infer_conqueror(loser)
        if conqueror in (Country.NONE, loser) or conqueror in self.defeated_countries:
            conqueror = self.infer_conqueror(loser)
        if conqueror in (Country.NONE, loser):
            return

        transferred = 0
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.grid[x][y]
                if cell.country == loser:
                    cell.country = conqueror
                    transferred += 1
                if cell.is_city and cell.city_owner == loser:
                    cell.city_owner = conqueror
                if cell.army and cell.army.country == loser:
                    cell.army.country = conqueror

        loser_player = self.players[loser]
        loot = max(0, int(loser_player.gold * DEFEAT_LOOT_RATIO))
        loser_player.gold = max(0, loser_player.gold - loot)
        if conqueror != Country.NONE:
            self.players[conqueror].gold += loot
            self.gold_looted[conqueror] = self.gold_looted.get(conqueror, 0) + loot

        self.defeated_countries.add(loser)
        self.occupation_tracker.pop(loser, None)
        self.log_event(
            f"{COUNTRY_NAMES[conqueror]} absorbe {COUNTRY_NAMES[loser]} "
            f"(+{loot} or, {transferred} cases)"
        )

        if loser == Country.RED and self.game_mode == "solo" and not self.is_game_over():
            self.player_defeated = True
            self.game_over_message = "Défaite : votre royaume est éliminé"
            self.audio.play("defeat")

    def update_defeat_states(self):
        for country in [Country.RED, Country.GREEN, Country.BLUE, Country.YELLOW, Country.ORANGE]:
            if country in self.defeated_countries:
                continue
            if self.country_has_anything(country):
                continue
            self.eliminate_country(country)

    def research_next_tech(self):
        player = self.players[self.current_player_country]
        tech = player.research_next()
        if tech is None:
            next_tech = player.get_next_tech()
            if next_tech is None:
                self.log_event("Tech tree deja complete")
            else:
                self.log_event(f"Pas assez d'or pour {next_tech['name']} ({next_tech['cost']})")
            return
        self.log_event(f"{COUNTRY_NAMES[player.country]} débloque {tech['name']}")

    def _get_loser_urban_cells(self, loser):
        urban_cells = []
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.grid[x][y]
                if cell.is_capital and cell.capital_owner == loser:
                    urban_cells.append(cell)
                elif cell.is_city and cell.city_owner == loser:
                    urban_cells.append(cell)
        return urban_cells

    def evaluate_occupation_pressure(self):
        """Annex immediately when ALL capitals/cities of a realm are occupied by one foe."""
        if self.turn_number < 5:
            return
        countries = [Country.RED, Country.GREEN, Country.BLUE, Country.YELLOW, Country.ORANGE]
        for loser in countries:
            if loser in self.defeated_countries:
                continue

            urban_cells = self._get_loser_urban_cells(loser)
            if not urban_cells:
                continue

            occupied_cells = [
                cell
                for cell in urban_cells
                if cell.country not in (loser, Country.NONE)
            ]
            if len(occupied_cells) != len(urban_cells):
                continue

            occupiers = {cell.country for cell in occupied_cells}
            if len(occupiers) != 1:
                continue

            occupier = next(iter(occupiers))

            transferred = 0
            for x in range(GRID_COLS):
                for y in range(GRID_ROWS):
                    cell = self.grid[x][y]
                    if cell.country == loser:
                        cell.country = occupier
                        transferred += 1
                    if cell.army and cell.army.country == loser:
                        cell.army.country = occupier

            loser_player = self.players[loser]
            occupier_player = self.players[occupier]
            loot = max(0, int(loser_player.gold * DEFEAT_LOOT_RATIO))
            loser_player.gold -= loot
            occupier_player.gold += loot
            self.gold_looted[occupier] = self.gold_looted.get(occupier, 0) + loot

            self.log_event(
                f"{COUNTRY_NAMES[occupier]} prend {COUNTRY_NAMES[loser]} (+{loot} or, {transferred} cases)"
            )
            self.defeated_countries.add(loser)
            self.check_victory()

    def init_players(self):
        """Initialise les joueurs selon le mode de jeu"""
        self.players = {}
        cfg = self.difficulty_cfg

        for country in [Country.RED, Country.GREEN, Country.BLUE, Country.YELLOW, Country.ORANGE]:
            player = Player(country)

            if self.game_mode == "solo" and country != SOLO_HUMAN_COUNTRY:
                player.is_ai = True
                player.gold = cfg["ai_gold"]
            elif self.game_mode == "solo" and country == SOLO_HUMAN_COUNTRY:
                player.gold = cfg["human_gold"]
            elif self.game_mode == "godgame":
                player.gold = cfg["human_gold"]

            self.players[country] = player

        self.current_player_country = Country.RED
        self.turn_number = 1

        self.log_event(f"Partie demarree en mode {self.game_mode}")
        for country, player in self.players.items():
            print(f"  {player} (IA: {player.is_ai})")

    def is_game_over(self):
        return self.winner_country is not None or self.player_defeated

    def get_viewer_country(self):
        """Pays utilisé pour le brouillard (solo = toujours le joueur humain)."""
        if self.game_mode == "solo":
            return SOLO_HUMAN_COUNTRY
        return self.current_player_country

    def get_ui_country(self):
        """Pays dont on affiche l'or et les actions (solo = Rouge)."""
        if self.game_mode == "solo":
            return SOLO_HUMAN_COUNTRY
        return self.current_player_country

    def is_human_turn(self):
        if self.game_mode == "godgame":
            return True
        return self.current_player_country == SOLO_HUMAN_COUNTRY and not self.ai_turn_pending

    def count_idle_armies(self, country):
        idle = 0
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                army = self.grid[x][y].army
                if army and army.country == country and army.movement_left > 0:
                    idle += 1
        return idle

    def idle_army_cells(self, country):
        cells = []
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.grid[x][y]
                if cell.army and cell.army.country == country and cell.army.movement_left > 0:
                    cells.append(cell)
        return cells

    def select_next_idle_army(self):
        country = self.current_player_country
        idle = self.idle_army_cells(country)
        if not idle:
            self.clear_order_modes()
            return False
        current = self.selected_cell
        nxt = idle[0]
        if current in idle:
            nxt = idle[(idle.index(current) + 1) % len(idle)]
        if self.selected_cell:
            self.selected_cell.is_selected = False
        self.selected_cell = nxt
        nxt.is_selected = True
        self.select_army_for_orders(nxt)
        self.log_event(f"{UNIT_NAMES[nxt.army.unit_type]} sélectionné")
        return True

    def maybe_advance_after_orders(self):
        if not self.is_human_turn():
            return
        cell = self.selected_cell
        if cell and cell.army and cell.army.country == self.current_player_country and cell.army.movement_left > 0:
            self.select_army_for_orders(cell)
            return
        self.select_next_idle_army()

    def get_ai_turn_delay_ms(self):
        return AI_SPEED_DELAYS_MS.get(self.settings.get("ai_speed", "normal"), 1000)

    def next_turn(self):
        """Passe au tour suivant"""
        if self.is_game_over() or self.pause_menu.open or self.fx.is_busy():
            return

        self.update_defeat_states()

        # Liste des pays dans l'ordre
        countries = [Country.RED, Country.GREEN, Country.BLUE, Country.YELLOW, Country.ORANGE]
        current_index = countries.index(self.current_player_country)

        next_country = self.current_player_country
        for step in range(1, len(countries) + 1):
            candidate = countries[(current_index + step) % len(countries)]
            if candidate not in self.defeated_countries:
                next_country = candidate
                break
        self.current_player_country = next_country
    
        # Si on revient au premier joueur, incrémente le numéro de tour
        if self.current_player_country == Country.RED:
            self.turn_number += 1
            print(f"\n=== Tour {self.turn_number} ===")
    
        # Génère l'or pour le joueur actuel
        self.generate_income()
        self.reset_army_moves_for_country(self.current_player_country)
        self.evaluate_occupation_pressure()
        self.check_victory()
        if self.is_game_over():
            return
    
        self.log_event(f"Tour de {COUNTRY_NAMES[self.current_player_country]}")
        self.fx.show_banner(f"Tour de {COUNTRY_NAMES[self.current_player_country]}")
        
        player = self.players[self.current_player_country]
        if self.current_player_country in self.defeated_countries:
            self.ai_turn_pending = True
            self.ai_turn_resume_at = pygame.time.get_ticks()
            return

        self._autosave()

        if player.is_ai:
            self.ai.play_turn(self.current_player_country)
            self.check_victory()
            if self.is_game_over():
                return
            self.ai_turn_pending = True
            self.ai_turn_resume_at = pygame.time.get_ticks() + self.get_ai_turn_delay_ms()
        elif self.is_human_turn():
            self.audio.play("turn")
            self.select_next_idle_army()

    def _autosave(self):
        if self.state != "playing":
            return
        try:
            save_game(self)
        except OSError as err:
            print(f"Autosave impossible: {err}")

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
        capital_income = capitals * (CAPITAL_INCOME + player.capital_income_bonus)
        city_income = cities * (CITY_INCOME + player.city_income_bonus)
        income = capital_income + city_income

        # Entretien des armées
        upkeep = player.calculate_upkeep(self.grid)

        # Total
        net_income = income - upkeep
        player.add_gold(net_income)
        player.gold = max(0, player.gold)
        self.last_income = income
        self.last_upkeep = upkeep

        self.log_event(f"{COUNTRY_NAMES[player.country]}: +{income} -{upkeep} = {net_income} or")

    def place_capitals_from_dict(self, capitals):
        for country, (x, y) in capitals.items():
            cell = self.grid[x][y]
            cell.is_capital = True
            cell.capital_owner = country
            cell.country = country
            if cell.terrain in (TerrainType.WATER, TerrainType.BEACH):
                cell.terrain = TerrainType.PLAIN

    def place_starting_armies(self):
        for country in [Country.RED, Country.GREEN, Country.BLUE, Country.YELLOW, Country.ORANGE]:
            for x in range(GRID_COLS):
                for y in range(GRID_ROWS):
                    cell = self.grid[x][y]
                    if cell.is_capital and cell.capital_owner == country:
                        cell.army = Army(country, UnitType.SWORDSMAN, 3)
                        player = self.players.get(country)
                        if player:
                            cell.army.refresh_movement(player)
                        break

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
                    try:
                        loaded = load_game(self)
                    except Exception as err:
                        loaded = False
                        print(f"Chargement impossible: {err}")
                    if loaded:
                        if hasattr(self, "audio") and self.audio:
                            self.audio.play_music("game")
                        self.log_event("Partie chargée")
                        self.audio.play("click")
                        self.select_next_idle_army()
                    else:
                        self.menu.load_error = "Pas de sauvegarde compatible (nouvelle partie requise)"
                        print(f"Aucune sauvegarde valide ({SAVE_PATH})")
                elif action == "quit":
                    self.running = False

            elif self.state == "playing":
                if self.tutorial.handle_event(event):
                    continue

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.selected_army_cell or self.bridge_mode or self.ranged_mode:
                        self.clear_order_modes()
                        continue
                    if not self.is_game_over():
                        if self.pause_menu.open and self.pause_menu.submenu == "settings":
                            self.pause_menu.leave_settings(self)
                        elif self.pause_menu.open:
                            self.pause_menu.close()
                        else:
                            self.pause_menu.toggle()
                        continue

                if self.pause_menu.open:
                    pause_action = self.pause_menu.handle_event(event, self)
                    if pause_action == "save":
                        self._autosave()
                        self.log_event("Partie sauvegardée")
                    elif pause_action == "quit_menu":
                        self._autosave()
                        self.state = "menu"
                        self.menu = Menu(self.screen)
                        self.pause_menu.close()
                        self.audio.play_music("menu")
                    continue

                if event.type == pygame.KEYDOWN and event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                    self._autosave()
                    self.log_event("Partie sauvegardée (Ctrl+S)")
                    continue

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.is_human_turn() and not self.fx.is_busy() and not self.is_game_over():
                        self.next_turn()
                    continue

                if event.type == pygame.KEYDOWN and event.key in (pygame.K_n, pygame.K_TAB):
                    if self.is_human_turn() and not self.fx.is_busy() and not self.is_game_over():
                        self.select_next_idle_army()
                    continue

                if self.is_game_over():
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.state = "menu"
                        self.menu = Menu(self.screen)
                        self.audio.play_music("menu")
                    elif event.type == pygame.KEYDOWN:
                        self.state = "menu"
                        self.menu = Menu(self.screen)
                        self.audio.play_music("menu")
                    continue

                if self.fx.is_busy():
                    continue

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    self.clear_order_modes()
                    continue

                if not self.is_human_turn():
                    continue

                ui_action = self.ui.handle_event(event, self)
                if ui_action == "end_turn":
                    self.next_turn()
                    continue
                elif ui_action == "next_unit":
                    self.select_next_idle_army()
                    continue
                elif ui_action == "build_city":
                    self.build_city()
                    continue
                elif ui_action == "build_bridge":
                    if not self.selected_cell or self.selected_cell.country != self.current_player_country:
                        self.log_event("Sélectionne une case alliée puis choisis Construire pont")
                    else:
                        self.bridge_mode = True
                        self.compute_bridge_targets()
                        self.log_event("Mode pont : clique une case d'eau en surbrillance")
                    continue
                elif ui_action == "research_next":
                    self.research_next_tech()
                    continue
                elif ui_action == "fortify":
                    self.fortify_selected_army()
                    self.maybe_advance_after_orders()
                    continue
                elif ui_action == "ranged_attack_mode":
                    if self.selected_cell and self.selected_cell.army:
                        self.select_army_for_orders(self.selected_cell)
                        self.log_event("Clique une cible violette")
                    continue
                elif ui_action == "disembark_mode":
                    cell = self.selected_cell
                    if cell and cell.army and (cell.x, cell.y) in self.get_disembark_targets(cell):
                        self.disembark_army(cell, cell)
                        self.clear_order_modes()
                        self.maybe_advance_after_orders()
                    elif cell and cell.army:
                        self.select_army_for_orders(cell)
                        self.log_event("Clique une plage ou une terre verte")
                    continue
                elif ui_action in ("move_army", "embark_mode"):
                    if self.selected_cell and self.selected_cell.army:
                        self.select_army_for_orders(self.selected_cell)
                    continue
                elif isinstance(ui_action, tuple) and ui_action[0] == "recruit":
                    self.recruit_unit(ui_action[1])
                    continue
                elif ui_action == "hud_click":
                    continue

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    coords = screen_to_cell(*event.pos)
                    if coords:
                        cell_x, cell_y = coords
                        if (cell_x, cell_y) not in self.visibility:
                            self.log_event("Zone non visible (brouillard)")
                            continue
                        clicked_cell = self.grid[cell_x][cell_y]
                        dest = (cell_x, cell_y)

                        if self.bridge_mode:
                            built = self.build_bridge_on_cell(clicked_cell)
                            if not built:
                                self.log_event("Pont impossible ici")
                            self.bridge_mode = False
                            self.bridge_targets.clear()
                            continue

                        if self.selected_army_cell and dest in self.ranged_targets:
                            self.ranged_attack(self.selected_army_cell, clicked_cell)
                            self.clear_order_modes()
                            self.maybe_advance_after_orders()
                            continue

                        order_tiles = self.move_targets | self.attack_targets | self.embark_targets | self.disembark_targets
                        if self.selected_army_cell and dest in order_tiles:
                            self.request_move(self.selected_army_cell, clicked_cell)
                            self.clear_order_modes()
                            continue

                        own_army = (
                            clicked_cell.army
                            and clicked_cell.army.country == self.current_player_country
                            and clicked_cell.army.movement_left > 0
                        )
                        if self.selected_cell:
                            self.selected_cell.is_selected = False
                        self.selected_cell = clicked_cell
                        self.selected_cell.is_selected = True
                        self.audio.play("click")
                        if own_army:
                            self.select_army_for_orders(clicked_cell)
                            self.log_event(f"{UNIT_NAMES[clicked_cell.army.unit_type]} sélectionné")
                        else:
                            self.clear_order_modes()
                            self.selected_cell = clicked_cell
                            self.selected_cell.is_selected = True
                            self.log_event(f"Case ({cell_x},{cell_y}) {TERRAIN_FULL_NAMES[clicked_cell.terrain]}")
                elif event.type == pygame.MOUSEMOTION:
                    coords = screen_to_cell(*event.pos)
                    if coords:
                        cell_x, cell_y = coords
                        self.hovered_cell = self.grid[cell_x][cell_y]
                        dest = (cell_x, cell_y)
                        if self.selected_army_cell and self.selected_army_cell.army and dest in self.visibility:
                            if dest in self.disembark_targets or dest in self.embark_targets:
                                self.preview_path_cells = [self.hovered_cell]
                            else:
                                self.preview_path_cells = self.find_path(
                                    self.selected_army_cell,
                                    self.hovered_cell,
                                    self.selected_army_cell.army.movement_left,
                                    self.selected_army_cell.army,
                                )
                        else:
                            self.preview_path_cells = []
                    else:
                        self.hovered_cell = None
                        self.preview_path_cells = []

    def compute_visibility(self):
        """Fog of war based on current player's units and owned territory."""
        if self.game_mode == "godgame":
            self.visibility = {(x, y) for x in range(GRID_COLS) for y in range(GRID_ROWS)}
            return

        viewer = self.get_viewer_country()
        visible = set()
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.grid[x][y]
                if cell.country == viewer:
                    visible.add((x, y))
                    cell.discovered_by.add(viewer)
                    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                            visible.add((nx, ny))
                            self.grid[nx][ny].discovered_by.add(viewer)
                is_source = (
                    (cell.country == viewer and (cell.is_city or cell.is_capital))
                    or (cell.army and cell.army.country == viewer)
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
                            self.grid[nx][ny].discovered_by.add(viewer)
        self.visibility = visible

    def update(self):
        for animation in self.animations:
            animation["ttl"] -= 1
        self.animations = [a for a in self.animations if a["ttl"] > 0]
        self.fx.update()

        if (
            self.state == "playing"
            and not self.pause_menu.open
            and self.ai_turn_pending
            and not self.is_game_over()
            and not self.fx.is_busy()
            and pygame.time.get_ticks() >= self.ai_turn_resume_at
        ):
            self.ai_turn_pending = False
            self.next_turn()

    def draw(self):
        if self.state == "menu":
            self.audio.play_music("menu")
            self.menu.draw()
            return

        if self.state == "playing":
            self.screen.fill((42, 32, 22))
            self.compute_visibility()
            tick = pygame.time.get_ticks()
            hidden = self.fx.hidden_army_cells()

            for x in range(GRID_COLS):
                for y in range(GRID_ROWS):
                    cell = self.grid[x][y]
                    is_visible = (x, y) in self.visibility
                    is_discovered = self.get_viewer_country() in cell.discovered_by
                    show_units = is_visible and (x, y) not in hidden
                    if is_visible:
                        cell.draw(self.screen, self.assets, show_units=show_units, tick=tick, grid=self.grid)
                    elif is_discovered:
                        cell.draw(self.screen, self.assets, show_units=False, tick=tick, grid=self.grid)
                    else:
                        pygame.draw.rect(
                            self.screen,
                            (18, 14, 10),
                            (*cell_screen_pos(x, y), CELL_SIZE, CELL_SIZE),
                        )

            if self.is_human_turn():
                pulse_a = 50 + int(40 * (0.5 + 0.5 * math.sin(tick / 180)))
                viewer = self.get_ui_country()
                for x in range(GRID_COLS):
                    for y in range(GRID_ROWS):
                        army = self.grid[x][y].army
                        if not army or army.country != viewer or army.movement_left <= 0:
                            continue
                        if (x, y) not in self.visibility:
                            continue
                        glow = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        pygame.draw.rect(
                            glow,
                            (212, 168, 78, pulse_a),
                            glow.get_rect().inflate(-8, -8),
                            2,
                        )
                        self.screen.blit(glow, cell_screen_pos(x, y))

            def blit_highlight(cells, fill, rim=None):
                for hx, hy in cells:
                    if (hx, hy) not in self.visibility:
                        continue
                    highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    highlight.fill(fill)
                    if rim:
                        pygame.draw.rect(highlight, rim, highlight.get_rect().inflate(-2, -2), 2)
                    self.screen.blit(highlight, cell_screen_pos(hx, hy))

            blit_highlight(self.move_targets, (48, 160, 62, 120), (230, 255, 210, 230))
            blit_highlight(self.attack_targets, (180, 36, 28, 130), (255, 190, 170, 240))
            blit_highlight(self.bridge_targets, (180, 140, 60, 110), (255, 220, 140, 220))
            blit_highlight(self.ranged_targets, (120, 60, 150, 120), (230, 190, 255, 230))
            blit_highlight(self.embark_targets, (36, 90, 140, 120), (170, 210, 255, 230))
            blit_highlight(self.disembark_targets, (40, 120, 70, 120), (190, 255, 190, 230))
            self.draw_movement_preview()

            for x in range(GRID_COLS):
                for y in range(GRID_ROWS):
                    cell = self.grid[x][y]
                    if (x, y) in self.visibility:
                        continue
                    fog_tile = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    if self.get_viewer_country() in cell.discovered_by:
                        fog_tile.fill((92, 72, 44, 150))
                    else:
                        fog_tile.fill((28, 20, 12, 245))
                    self.screen.blit(fog_tile, cell_screen_pos(x, y))

            for animation in self.animations:
                alpha = max(20, int(180 * (animation["ttl"] / animation["max_ttl"])))
                for ax, ay in animation["cells"]:
                    pulse = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    pulse.fill((*animation["color"], alpha))
                    self.screen.blit(pulse, cell_screen_pos(ax, ay))

            self.fx.draw(self.screen)
            self.ui.draw(self)
            self.draw_tooltip()
            self.tutorial.draw(self.screen)
            self.pause_menu.draw(self)
            if self.is_game_over():
                draw_end_recap(self.screen, self)
            pygame.display.flip()
    
    def run(self):
        while self.running:
            try:
                self.handle_events()
                self.update()
                self.draw()
            except Exception:
                import traceback
                traceback.print_exc()
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
        if not self.hovered_cell or not self.ui:
            return
        x, y = pygame.mouse.get_pos()
        if self.ui.blocks_map((x, y)):
            return
        if x >= MAP_PIXEL_WIDTH or y < MAP_ORIGIN_Y:
            return
        if (self.hovered_cell.x, self.hovered_cell.y) not in self.visibility:
            return

        cell = self.hovered_cell
        lines = [
            f"{TERRAIN_FULL_NAMES[cell.terrain]}  ({cell.x},{cell.y})",
            COUNTRY_NAMES[cell.country] if cell.country != Country.NONE else "Neutre",
        ]
        if cell.is_capital:
            lines.append("Capitale")
            lines.append(f"Murs +{CAPITAL_WALL_BONUS}. Garnison {CAPITAL_GARRISON_COUNT} lanciers")
        elif cell.is_city:
            lines.append("Ville")
            lines.append(f"Murs +{CITY_WALL_BONUS}. Garnison {CITY_GARRISON_COUNT} lanciers")
        move_cost = TERRAIN_MOVE_COST.get(cell.terrain, 1)
        if cell.terrain != TerrainType.WATER:
            lines.append(f"Coût de déplacement : {move_cost} PM")
        bonus = TERRAIN_DEFENSE_BONUS.get(cell.terrain, 0)
        if bonus:
            lines.append(f"Défense terrain +{bonus}")
        if cell.terrain == TerrainType.BRIDGE:
            lines.append(f"Pont  {cell.bridge_hp} PV")
        if cell.army:
            army = cell.army
            ship = " navire" if army.embarked else ""
            lines.append(
                f"{UNIT_NAMES[army.unit_type]}{ship}  x{army.count}"
            )
            lines.append(f"Mouvement {army.movement_left}/{army.movement_range(self.players.get(army.country))}")
            stats = UNIT_STATS[army.unit_type]
            lines.append(f"Att {stats['attack']}  Déf {stats['defense']}")
        dest = (cell.x, cell.y)
        if self.selected_army_cell and self.selected_army_cell.army:
            army = self.selected_army_cell.army
            cost = getattr(self, "move_costs", {}).get(dest)
            if dest in self.move_targets and cost is not None:
                left = max(0, army.movement_left - cost)
                if left <= 0:
                    lines.append(f"L'armée s'arrête ici ({cost} PM)")
                else:
                    lines.append(f"{cost} PM. Encore {left} après")
            elif dest in self.attack_targets:
                lines.append("Attaque : l'armée avance jusqu'ici")
            elif dest in self.embark_targets:
                lines.append("Embarquement : l'armée s'arrête sur l'eau")
            elif dest in self.disembark_targets:
                lines.append("Débarquement : l'armée s'arrête à terre")

        from theme import INK, PARCHMENT, GOLD, WOOD_DARK, load_font, draw_bevel_rect, wrap_text

        font = load_font(16)
        max_line = 240
        wrapped = []
        for line in lines:
            wrapped.extend(wrap_text(font, line, max_line))
        width = max(max_line, max(font.size(line)[0] for line in wrapped) + 20)
        height = len(wrapped) * 18 + 14
        tx = x + 16
        ty = y + 16
        if tx + width > MAP_PIXEL_WIDTH - 4:
            tx = x - width - 12
        if ty + height > WINDOW_HEIGHT - 4:
            ty = y - height - 12
        tx = max(4, min(tx, MAP_PIXEL_WIDTH - width - 4))
        ty = max(MAP_ORIGIN_Y + 4, min(ty, WINDOW_HEIGHT - height - 4))
        rect = pygame.Rect(tx, ty, width, height)
        draw_bevel_rect(self.screen, rect, PARCHMENT, GOLD, WOOD_DARK, 2)
        pygame.draw.rect(self.screen, GOLD, rect, 1)
        for idx, line in enumerate(wrapped):
            self.screen.blit(font.render(line, True, INK), (tx + 10, ty + 7 + idx * 18))

    def draw_movement_preview(self):
        """Chemin, limite de portée et fantôme d'arrivée."""
        from theme import CREAM, GOLD, GOLD_BRIGHT, INK, load_font

        army_cell = self.selected_army_cell
        if not army_cell or not army_cell.army or not self.is_human_turn():
            return
        army = army_cell.army
        max_range = army.movement_left
        costs = getattr(self, "move_costs", {})

        for (hx, hy), cost in costs.items():
            if (hx, hy) not in self.move_targets:
                continue
            if (hx, hy) not in self.visibility:
                continue
            if cost != max_range:
                continue
            rect = pygame.Rect(*cell_screen_pos(hx, hy), CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, GOLD, rect.inflate(-3, -3), 2)

        path = self.preview_path_cells or []
        if not path:
            return
        for cell in path[:-1]:
            if (cell.x, cell.y) not in self.visibility:
                continue
            cx, cy = cell_screen_pos(cell.x, cell.y)
            pygame.draw.circle(
                self.screen,
                CREAM,
                (cx + CELL_SIZE // 2, cy + CELL_SIZE // 2),
                5,
            )
            pygame.draw.circle(
                self.screen,
                INK,
                (cx + CELL_SIZE // 2, cy + CELL_SIZE // 2),
                5,
                1,
            )

        dest = path[-1]
        if (dest.x, dest.y) not in self.visibility:
            return
        dx, dy = cell_screen_pos(dest.x, dest.y)
        dest_rect = pygame.Rect(dx, dy, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, GOLD_BRIGHT, dest_rect.inflate(-1, -1), 3)
        pygame.draw.rect(self.screen, INK, dest_rect.inflate(-4, -4), 1)

        ghost = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        draw_army_at(ghost, 0, 0, army, self.assets)
        ghost.set_alpha(155)
        self.screen.blit(ghost, (dx, dy))

        cost = costs.get((dest.x, dest.y), len(path))
        left = max(0, max_range - cost)
        font = load_font(14, bold=True)
        label = "Arrêt" if left <= 0 else f"reste {left}"
        text = font.render(label, True, INK)
        pad = pygame.Rect(0, 0, text.get_width() + 8, text.get_height() + 4)
        pad.midbottom = (dx + CELL_SIZE // 2, dy - 2)
        if pad.top < HUD_TOP:
            pad.midtop = (dx + CELL_SIZE // 2, dy + CELL_SIZE + 2)
        pygame.draw.rect(self.screen, GOLD_BRIGHT, pad)
        pygame.draw.rect(self.screen, INK, pad, 1)
        self.screen.blit(text, text.get_rect(center=pad.center))


if __name__ == "__main__":
    game = Game()
    game.run()