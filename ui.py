import pygame
from constants import *
from menu import Button

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 28)
        self.font_normal = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        
        # Position du panneau
        self.panel_x = GRID_COLS * CELL_SIZE
        self.panel_y = 0
        self.panel_width = UI_WIDTH
        self.panel_height = WINDOW_HEIGHT

        # Bouton fin de tour
        button_width = 200
        button_height = 50
        self.btn_end_turn = Button(
            self.panel_x + (UI_WIDTH - button_width) // 2,
            WINDOW_HEIGHT - 80,
            button_width,
            button_height,
            "Fin de tour",
            (39, 174, 96),
            (46, 204, 113)
        )
        
        # Boutons d'action
        recruit_y = 560
        button_small_width = UI_WIDTH - 50
        button_small_height = 30
        spacing = 5

        self.btn_recruit_swordsman = Button(
            self.panel_x + 25,
            recruit_y,
            button_small_width,
            button_small_height,
            f"Spadassin ({UNIT_COSTS[UnitType.SWORDSMAN]} or)",
            (41, 128, 185),
            (52, 152, 219)
        )

        self.btn_recruit_crossbowman = Button(
            self.panel_x + 25,
            recruit_y + button_small_height + spacing,
            button_small_width,
            button_small_height,
            f"Arbalétrier ({UNIT_COSTS[UnitType.CROSSBOWMAN]} or)",
            (142, 68, 173),
            (155, 89, 182)
        )

        self.btn_recruit_cavalry = Button(
            self.panel_x + 25,
            recruit_y + (button_small_height + spacing) * 2,
            button_small_width,
            button_small_height,
            f"Cavalerie ({UNIT_COSTS[UnitType.CAVALRY]} or)",
            (230, 126, 34),
            (243, 156, 18)
        )

        # Bouton construction ville
        self.btn_build_city = Button(
            self.panel_x + 25,
            recruit_y + (button_small_height + spacing) * 3,
            button_small_width,
            button_small_height,
            f"Construire ville (150 or)",
            (39, 174, 96),
            (46, 204, 113)
        )

        # Bouton construction pont
        self.btn_build_bridge = Button(
            self.panel_x + 25,
            recruit_y + (button_small_height + spacing) * 4,
            button_small_width,
            button_small_height,
            f"Construire pont ({BRIDGE_COST} or)",
            (127, 101, 65),
            (148, 122, 86)
        )

        # Bouton déplacement
        self.btn_move_army = Button(
            self.panel_x + 25,
            recruit_y + (button_small_height + spacing) * 5,
            button_small_width,
            button_small_height,
            "Deplacer armee",
            (52, 73, 94),
            (71, 94, 121)
        )

        self.btn_ranged_attack = Button(
            self.panel_x + 25,
            recruit_y + (button_small_height + spacing) * 6,
            button_small_width,
            button_small_height,
            "Tir a distance",
            (120, 70, 170),
            (140, 90, 190),
        )

        self.btn_fortify = Button(
            self.panel_x + 25,
            recruit_y + (button_small_height + spacing) * 7,
            button_small_width,
            button_small_height,
            "Fortifier",
            (80, 110, 90),
            (96, 130, 108),
        )
        self.btn_research = Button(
            self.panel_x + 25,
            WINDOW_HEIGHT - 150,
            button_small_width,
            34,
            "Rechercher tech",
            (90, 110, 150),
            (105, 130, 170),
        )

        self.current_tab = "actions"
        tab_width = (UI_WIDTH - 60) // 3
        self.btn_tab_actions = Button(self.panel_x + 20, 500, tab_width, 28, "Actions", (70, 80, 95), (90, 100, 115))
        self.btn_tab_events = Button(self.panel_x + 25 + tab_width, 500, tab_width, 28, "Events", (70, 80, 95), (90, 100, 115))
        self.btn_tab_stats = Button(self.panel_x + 30 + tab_width * 2, 500, tab_width, 28, "Stats", (70, 80, 95), (90, 100, 115))

    def draw(self, game):
        # Fond du panneau
        pygame.draw.rect(self.screen, UI_BG_COLOR, 
                        (self.panel_x, self.panel_y, self.panel_width, self.panel_height))

        # Ligne de séparation
        pygame.draw.line(self.screen, (80, 80, 85), 
                        (self.panel_x, 0), (self.panel_x, WINDOW_HEIGHT), 2)

        y_offset = 20

        # Top bar stratégique
        bar_height = 36
        pygame.draw.rect(self.screen, (28, 30, 35), (0, 0, GRID_COLS * CELL_SIZE, bar_height))
        top_text = self.font_small.render(
            f"Tour {game.turn_number} | {COUNTRY_NAMES[game.current_player_country]} | Or {game.players[game.current_player_country].gold} | Revenus {game.last_income} | Entretien {game.last_upkeep}",
            True,
            (220, 220, 220),
        )
        self.screen.blit(top_text, (10, 10))

        # Titre
        title = self.font_title.render("The World Is Ours", True, UI_TITLE_COLOR)
        self.screen.blit(title, (self.panel_x + 20, y_offset))
        y_offset += 40

        # Numéro de tour
        turn_text = self.font_small.render(f"Tour: {game.turn_number}", True, (150, 150, 150))
        self.screen.blit(turn_text, (self.panel_x + 20, y_offset))
        y_offset += 40

        if game.winner_country:
            winner_text = self.font_normal.render(
                f"Victoire: {COUNTRY_NAMES[game.winner_country]}",
                True,
                (255, 215, 0),
            )
            self.screen.blit(winner_text, (self.panel_x + 20, y_offset))
            y_offset += 40

        # Pays actuellement joué
        current_country = game.current_player_country
        player = game.players[current_country]
        self.draw_section_title("Pays actuel", y_offset)
        y_offset += 30

        # Nom et couleur du pays
        country_name = COUNTRY_NAMES[current_country]
        pygame.draw.circle(self.screen, COUNTRY_COLORS[current_country], 
                          (self.panel_x + 30, y_offset + 10), 8)
        text = self.font_normal.render(country_name, True, UI_TEXT_COLOR)
        self.screen.blit(text, (self.panel_x + 50, y_offset))
        y_offset += 35

        # Or
        gold = player.gold
        text = self.font_normal.render(f"Or: {gold}", True, (255, 215, 0))
        self.screen.blit(text, (self.panel_x + 30, y_offset))
        y_offset += 45

        # Infos case sélectionnée
        if game.selected_cell:
            self.draw_section_title("Case sélectionnée", y_offset)
            y_offset += 30

            cell = game.selected_cell

            # Position
            text = self.font_small.render(f"Position: ({cell.x}, {cell.y})", True, UI_TEXT_COLOR)
            self.screen.blit(text, (self.panel_x + 30, y_offset))
            y_offset += 22

            # Terrain
            terrain_name = TERRAIN_FULL_NAMES[cell.terrain]
            text = self.font_small.render(f"Terrain: {terrain_name}", True, UI_TEXT_COLOR)
            self.screen.blit(text, (self.panel_x + 30, y_offset))
            y_offset += 22

            # Pays
            if cell.country != Country.NONE:
                country_name = COUNTRY_NAMES[cell.country]
                pygame.draw.circle(self.screen, COUNTRY_COLORS[cell.country], 
                                 (self.panel_x + 40, y_offset + 8), 6)
                text = self.font_small.render(country_name, True, UI_TEXT_COLOR)
                self.screen.blit(text, (self.panel_x + 55, y_offset))
                y_offset += 22
            else:
                text = self.font_small.render("Pays: Neutre", True, UI_TEXT_COLOR)
                self.screen.blit(text, (self.panel_x + 30, y_offset))
                y_offset += 22

            # Capitale
            if cell.is_capital:
                text = self.font_small.render("⭐ Capitale", True, (255, 215, 0))
                self.screen.blit(text, (self.panel_x + 30, y_offset))
                y_offset += 22

            # Ville
            if cell.is_city:
                text = self.font_small.render("🏘 Ville", True, (100, 200, 100))
                self.screen.blit(text, (self.panel_x + 30, y_offset))
                y_offset += 22

            # Armée
            if cell.army:
                y_offset += 5
                army_name = UNIT_NAMES[cell.army.unit_type]
                symbol = UNIT_SYMBOLS[cell.army.unit_type]
                text = self.font_small.render(
                    f"{symbol} {army_name} x{cell.army.count}/{MAX_UNITS_PER_ARMY}",
                    True,
                    (255, 255, 100),
                )
                self.screen.blit(text, (self.panel_x + 30, y_offset))
                y_offset += 22

                move_range = UNIT_MOVEMENT_RANGE.get(cell.army.unit_type, MOVEMENT_RANGE)
                move_text = self.font_small.render(
                    f"Portee: {move_range} | PM restant: {cell.army.movement_left}",
                    True,
                    UI_TEXT_COLOR,
                )
                self.screen.blit(move_text, (self.panel_x + 30, y_offset))
                y_offset += 22
                status = "Deja deplacee" if cell.army.movement_left <= 0 else "Prete"
                status_text = self.font_small.render(f"Etat: {status}", True, UI_TEXT_COLOR)
                self.screen.blit(status_text, (self.panel_x + 30, y_offset))
                y_offset += 22
                if cell.army.is_fortified:
                    fort = self.font_small.render("Fortifiee (+def)", True, (180, 220, 180))
                    self.screen.blit(fort, (self.panel_x + 30, y_offset))
                    y_offset += 22

            y_offset += 20

        # Tabs
        self.btn_tab_actions.draw(self.screen, self.font_small)
        self.btn_tab_events.draw(self.screen, self.font_small)
        self.btn_tab_stats.draw(self.screen, self.font_small)
        recruit_y = 560
        self.draw_section_title(self.current_tab.capitalize(), recruit_y - 36)
        recruit_y += 10

        # Affiche les boutons selon contexte de la case sélectionnée
        if self.current_tab == "actions" and game.selected_cell:
            can_recruit = (
                game.selected_cell.country == current_country
                and (game.selected_cell.is_city or game.selected_cell.is_capital)
                and game.selected_cell.terrain not in (TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE)
            )
            can_build_city = (
                game.selected_cell.country == current_country
                and not game.selected_cell.is_city
                and not game.selected_cell.is_capital
                and game.selected_cell.terrain not in (TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE)
                and not game.selected_cell.army
            )
            can_build_bridge = (
                game.selected_cell.country == current_country
                and game.selected_cell.terrain != TerrainType.WATER
            )
            can_move = game.selected_cell.army and game.selected_cell.army.country == current_country

            if can_recruit:
                self.btn_recruit_swordsman.draw(self.screen, self.font_small)
                self.btn_recruit_crossbowman.draw(self.screen, self.font_small)
                self.btn_recruit_cavalry.draw(self.screen, self.font_small)
            if can_build_city:
                self.btn_build_city.draw(self.screen, self.font_small)
            if can_build_bridge:
                self.btn_build_bridge.draw(self.screen, self.font_small)
                if game.bridge_mode:
                    bridge_msg = self.font_small.render("Mode pont actif: clique eau", True, (230, 200, 140))
                    self.screen.blit(bridge_msg, (self.panel_x + 28, recruit_y + 246))

            if not (can_recruit or can_build_city or can_build_bridge or can_move):
                msg = self.font_small.render("Aucune action disponible ici", True, (150, 150, 150))
                self.screen.blit(msg, (self.panel_x + 28, recruit_y + 22))

            if can_move:
                self.btn_move_army.draw(self.screen, self.font_small)
                self.btn_fortify.draw(self.screen, self.font_small)
                if game.selected_cell.army.unit_type == UnitType.CROSSBOWMAN:
                    self.btn_ranged_attack.draw(self.screen, self.font_small)
                if game.selected_cell.army.movement_left <= 0:
                    moved_msg = self.font_small.render("Cette armee a deja bouge", True, (220, 120, 120))
                    self.screen.blit(moved_msg, (self.panel_x + 30, recruit_y + 240))
        elif self.current_tab == "actions":
            # Message si pas de case sélectionnée
            msg = self.font_small.render("Sélectionnez une", True, (150, 150, 150))
            msg2 = self.font_small.render("case pour recruter", True, (150, 150, 150))
            self.screen.blit(msg, (self.panel_x + 60, recruit_y + 30))
            self.screen.blit(msg2, (self.panel_x + 50, recruit_y + 50))
        elif self.current_tab == "events":
            y = recruit_y
            for msg in game.event_log[-10:]:
                clipped = msg[:44]
                line = self.font_small.render(clipped, True, (190, 190, 190))
                self.screen.blit(line, (self.panel_x + 24, y))
                y += 20
        else:
            y = recruit_y
            territories = self.count_territories(game)
            for country, count in territories.items():
                if country == Country.NONE or count <= 0:
                    continue
                pygame.draw.circle(self.screen, COUNTRY_COLORS[country], (self.panel_x + 30, y + 8), 6)
                text = self.font_small.render(f"{COUNTRY_NAMES[country]}: {count} cases", True, UI_TEXT_COLOR)
                self.screen.blit(text, (self.panel_x + 45, y))
                y += 20
            y += 10
            player = game.players[current_country]
            tech_title = self.font_small.render("Techs:", True, (190, 210, 230))
            self.screen.blit(tech_title, (self.panel_x + 24, y))
            y += 20
            if player.unlocked_techs:
                for tech in TECH_TREE:
                    if tech["id"] not in player.unlocked_techs:
                        continue
                    line = self.font_small.render(f"- {tech['name']}", True, (170, 220, 170))
                    self.screen.blit(line, (self.panel_x + 30, y))
                    y += 18
            else:
                line = self.font_small.render("- Aucune", True, (150, 150, 150))
                self.screen.blit(line, (self.panel_x + 30, y))

        # Bouton fin de tour
        self.btn_research.draw(self.screen, self.font_small)
        next_tech = game.players[current_country].get_next_tech()
        if next_tech:
            line = self.font_small.render(
                f"Tech: {next_tech['name']} ({next_tech['cost']} or)",
                True,
                (170, 190, 220),
            )
        else:
            line = self.font_small.render("Tech tree complete", True, (170, 220, 170))
        self.screen.blit(line, (self.panel_x + 28, WINDOW_HEIGHT - 112))

        self.btn_end_turn.draw(self.screen, self.font_normal)
    
    def handle_event(self, event, game):
        """Gère les événements UI"""
        if self.btn_end_turn.handle_event(event):
            return "end_turn"
        if self.btn_research.handle_event(event):
            return "research_next"
        if self.btn_tab_actions.handle_event(event):
            self.current_tab = "actions"
            return None
        if self.btn_tab_events.handle_event(event):
            self.current_tab = "events"
            return None
        if self.btn_tab_stats.handle_event(event):
            self.current_tab = "stats"
            return None

        selected_cell = game.selected_cell
        current_country = game.current_player_country
        can_recruit = (
            selected_cell
            and selected_cell.country == current_country
            and (selected_cell.is_city or selected_cell.is_capital)
            and selected_cell.terrain not in (TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE)
        )
        can_build_city = (
            selected_cell
            and selected_cell.country == current_country
            and not selected_cell.is_city
            and not selected_cell.is_capital
            and selected_cell.terrain not in (TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE)
            and not selected_cell.army
        )
        can_build_bridge = (
            selected_cell
            and selected_cell.country == current_country
            and selected_cell.terrain != TerrainType.WATER
        )
        can_move = selected_cell and selected_cell.army and selected_cell.army.country == current_country

        # Construction ville
        if can_build_city and self.btn_build_city.handle_event(event):
            return "build_city"
        if can_build_bridge and self.btn_build_bridge.handle_event(event):
            return "build_bridge"
        
        # Déplacement
        if can_move and self.btn_move_army.handle_event(event):
            return "move_army"
        if can_move and self.btn_fortify.handle_event(event):
            return "fortify"
        if (
            can_move
            and selected_cell.army.unit_type == UnitType.CROSSBOWMAN
            and self.btn_ranged_attack.handle_event(event)
        ):
            return "ranged_attack_mode"

        # Recrutement
        if can_recruit and self.btn_recruit_swordsman.handle_event(event):
            return ("recruit", UnitType.SWORDSMAN)
        if can_recruit and self.btn_recruit_crossbowman.handle_event(event):
            return ("recruit", UnitType.CROSSBOWMAN)
        if can_recruit and self.btn_recruit_cavalry.handle_event(event):
            return ("recruit", UnitType.CAVALRY)
        
        return None

    def draw_section_title(self, title, y):
        text = self.font_normal.render(title, True, UI_TITLE_COLOR)
        self.screen.blit(text, (self.panel_x + 20, y))
        # Ligne sous le titre
        pygame.draw.line(self.screen, (80, 80, 85), 
                        (self.panel_x + 20, y + 25), 
                        (self.panel_x + UI_WIDTH - 20, y + 25), 1)
    
    def count_territories(self, game):
        counts = {country: 0 for country in Country}
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = game.grid[x][y]
                if cell.country != Country.NONE:
                    counts[cell.country] += 1
        return counts