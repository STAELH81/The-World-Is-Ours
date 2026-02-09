import pygame
import sys
from constants import *
from cell import Cell
from ui import UI
from menu import Menu
from army import Army
from player import Player
from ai import AI


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("The World Is Ours")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # États du jeu
        self.state = "menu"  # menu, playing
        self.game_mode = None  # solo, godgame
        
        # Menu
        self.menu = Menu(self.screen)
        
        # Grille de cellules (sera initialisée au démarrage du jeu)
        self.grid = None
        self.selected_cell = None
        self.ui = None

        # Joueurs
        self.players = {}
        self.current_player_country = Country.RED
        self.turn_number = 1

        # Grille de cellules (sera initialisée au démarrage du jeu)
        self.grid = None
        self.selected_cell = None
        self.selected_army_cell = None  # NOUVEAU : case avec armée sélectionnée pour mouvement
        self.ui = None
        self.ai = None  # Sera initialisé au démarrage

    def start_game(self, mode):
        """Démarre une nouvelle partie"""
        self.game_mode = mode
        self.state = "playing"
        
        # Initialise le jeu
        self.grid = [[Cell(x, y) for y in range(GRID_ROWS)] for x in range(GRID_COLS)]
        self.selected_cell = None
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

        if cell.terrain == TerrainType.WATER or cell.terrain == TerrainType.BEACH:
            print("Impossible de recruter sur l'eau ou la plage")
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

        print(f"✓ {UNIT_NAMES[unit_type]} recruté ! Or restant: {player.gold}")
    
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

        if cell.terrain == TerrainType.WATER or cell.terrain == TerrainType.BEACH:
            print("Impossible de construire sur l'eau ou la plage")
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

        print(f"✓ Ville construite ! Or restant: {player.gold} - Villes: {current_cities + 1}/{max_cities}")

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

        if to_cell.terrain == TerrainType.WATER:
            print("Impossible de se déplacer sur l'eau")
            return

        # Calcul de distance (Manhattan)
        distance = abs(from_cell.x - to_cell.x) + abs(from_cell.y - to_cell.y)
        if distance > MOVEMENT_RANGE:
            print(f"Trop loin ! Distance max: {MOVEMENT_RANGE}")
            return

        # Si case ennemie avec armée → COMBAT
        if to_cell.army and to_cell.army.country != self.current_player_country:
            self.battle(from_cell, to_cell)
            return

        # Si case ennemie vide → CONQUÊTE + DÉPLACEMENT
        if to_cell.country != Country.NONE and to_cell.country != self.current_player_country:
            print(f"⚔️ Conquête de {COUNTRY_NAMES[to_cell.country]} !")
            to_cell.country = self.current_player_country

        # Déplacement simple
        if to_cell.army:
            # Fusion d'armées du même type
            if to_cell.army.unit_type == army.unit_type:
                to_cell.army.count += army.count
                from_cell.army = None
                print(f"✓ Armées fusionnées ! ({to_cell.army.count} {UNIT_NAMES[army.unit_type]})")
            else:
                print("Impossible de fusionner des types d'unités différents")
                return
        else:
            # Déplacement simple
            to_cell.army = army
            from_cell.army = None
            print(f"✓ Déplacement effectué")

    def battle(self, attacker_cell, defender_cell):
        """Gère un combat entre deux armées"""
        attacker = attacker_cell.army
        defender = defender_cell.army

        print(f"\n⚔️ COMBAT ! {COUNTRY_NAMES[attacker.country]} vs {COUNTRY_NAMES[defender.country]}")
        print(f"  Attaquant: {attacker.count}x {UNIT_NAMES[attacker.unit_type]}")
        print(f"  Défenseur: {defender.count}x {UNIT_NAMES[defender.unit_type]} (Terrain: {defender_cell.terrain.name})")

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

            print(f"✓ {COUNTRY_NAMES[attacker.country]} gagne ! (pertes: {losses})")

            # Conquête
            defender_cell.country = attacker.country
            defender_cell.army = attacker
            attacker_cell.army = None

        elif defender_power > attacker_power:
            # Victoire défenseur
            losses = max(1, attacker.count // 2)
            defender.count = max(1, defender.count - losses)

            print(f"✓ {COUNTRY_NAMES[defender.country]} défend avec succès ! (pertes: {losses})")

            # Attaquant détruit
            attacker_cell.army = None

        else:
            # Égalité - les deux perdent des unités
            attacker.count = max(1, attacker.count - 1)
            defender.count = max(1, defender.count - 1)

            print(f"⚔️ Combat indécis ! Les deux camps subissent des pertes")

            # Attaquant ne bouge pas

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

        print(f"Partie démarrée en mode {self.game_mode}")
        for country, player in self.players.items():
            print(f"  {player} (IA: {player.is_ai})")

    def next_turn(self):
        """Passe au tour suivant"""
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
    
        print(f"C'est au tour de {COUNTRY_NAMES[self.current_player_country]}")
        
        # Si c'est un joueur IA, joue automatiquement
        player = self.players[self.current_player_country]
        if player.is_ai:
            self.ai.play_turn(self.current_player_country)
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

        print(f"{COUNTRY_NAMES[player.country]} : +{capital_income} (Cap) +{city_income} (Villes) -{upkeep} (Entr) = {net_income} or net")

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
                # Gestion UI
                ui_action = self.ui.handle_event(event)
                if ui_action == "end_turn":
                    self.next_turn()
                    continue
                elif ui_action == "build_city":
                    self.build_city()
                    continue
                elif ui_action == "move_army":
                    if self.selected_cell and self.selected_cell.army:
                        self.selected_army_cell = self.selected_cell
                        print(f"➡️ Cliquez sur une case pour déplacer {UNIT_NAMES[self.selected_cell.army.unit_type]}")
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
                        clicked_cell = self.grid[cell_x][cell_y]

                        # Si on a déjà une armée sélectionnée pour le mouvement
                        if self.selected_army_cell:
                            # Tente de déplacer vers la case cliquée
                            self.move_army(self.selected_army_cell, clicked_cell)
                            self.selected_army_cell = None

                        # Sinon, sélection normale
                        else:
                            if self.selected_cell:
                                self.selected_cell.is_selected = False

                            self.selected_cell = clicked_cell
                            self.selected_cell.is_selected = True

                            print(f"Case ({cell_x}, {cell_y}) - Terrain: {self.selected_cell.terrain.name} - Pays: {self.selected_cell.country.name}")

    def update(self):
        pass
    
    def draw(self):
        if self.state == "menu":
            self.menu.draw()
        
        elif self.state == "playing":
            self.screen.fill((0, 0, 0))
            
            for x in range(GRID_COLS):
                for y in range(GRID_ROWS):
                    self.grid[x][y].draw(self.screen)
            
            self.ui.draw(self)
            
            pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()