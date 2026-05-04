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
        recruit_y = WINDOW_HEIGHT - 350
        button_small_width = UI_WIDTH - 50
        button_small_height = 40
        spacing = 10

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
                text = self.font_small.render(f"{symbol} {army_name} x{cell.army.count}", True, (255, 255, 100))
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

            y_offset += 20

        # Stats globales
        recruit_y = WINDOW_HEIGHT - 350
        max_content_y = recruit_y - 120

        self.draw_section_title("Statistiques", y_offset)
        y_offset += 30

        # Compte les territoires par pays
        territories = self.count_territories(game)
        for country, count in territories.items():
            if y_offset > max_content_y:
                more = self.font_small.render("...", True, (150, 150, 150))
                self.screen.blit(more, (self.panel_x + 30, y_offset))
                break
            if country != Country.NONE and count > 0:
                pygame.draw.circle(self.screen, COUNTRY_COLORS[country], 
                                 (self.panel_x + 30, y_offset + 8), 6)
                text = self.font_small.render(f"{count} cases", True, UI_TEXT_COLOR)
                self.screen.blit(text, (self.panel_x + 45, y_offset))
                y_offset += 20

        # Event panel
        y_offset += 10
        self.draw_section_title("Evenements", y_offset)
        y_offset += 30
        for msg in game.event_log[-4:]:
            clipped = msg[:42]
            line = self.font_small.render(clipped, True, (190, 190, 190))
            self.screen.blit(line, (self.panel_x + 24, y_offset))
            y_offset += 18

        # Section recrutement
        self.draw_section_title("Recrutement", recruit_y)
        recruit_y += 35

        # Affiche les boutons seulement si une case du joueur est sélectionnée
        if game.selected_cell:
            can_recruit = game.selected_cell.country == current_country
            can_move = game.selected_cell.army and game.selected_cell.army.country == current_country

            if can_recruit:
                self.btn_recruit_swordsman.draw(self.screen, self.font_small)
                self.btn_recruit_crossbowman.draw(self.screen, self.font_small)
                self.btn_recruit_cavalry.draw(self.screen, self.font_small)
                self.btn_build_city.draw(self.screen, self.font_small)
                self.btn_build_bridge.draw(self.screen, self.font_small)
                if game.bridge_mode:
                    bridge_msg = self.font_small.render("Mode pont actif: clique eau", True, (230, 200, 140))
                    self.screen.blit(bridge_msg, (self.panel_x + 28, recruit_y + 246))
            else:
                msg = self.font_small.render("Recrutement: case non alliee", True, (150, 150, 150))
                self.screen.blit(msg, (self.panel_x + 28, recruit_y + 22))

            if can_move:
                self.btn_move_army.draw(self.screen, self.font_small)
                if game.selected_cell.army.movement_left <= 0:
                    moved_msg = self.font_small.render("Cette armee a deja bouge", True, (220, 120, 120))
                    self.screen.blit(moved_msg, (self.panel_x + 30, recruit_y + 240))
        else:
            # Message si pas de case sélectionnée
            msg = self.font_small.render("Sélectionnez une", True, (150, 150, 150))
            msg2 = self.font_small.render("case pour recruter", True, (150, 150, 150))
            self.screen.blit(msg, (self.panel_x + 60, recruit_y + 30))
            self.screen.blit(msg2, (self.panel_x + 50, recruit_y + 50))

        # Bouton fin de tour
        self.btn_end_turn.draw(self.screen, self.font_normal)
    
    def handle_event(self, event, game):
        """Gère les événements UI"""
        if self.btn_end_turn.handle_event(event):
            return "end_turn"

        selected_cell = game.selected_cell
        current_country = game.current_player_country
        can_recruit = selected_cell and selected_cell.country == current_country
        can_move = selected_cell and selected_cell.army and selected_cell.army.country == current_country

        # Construction ville
        if can_recruit and self.btn_build_city.handle_event(event):
            return "build_city"
        if can_recruit and self.btn_build_bridge.handle_event(event):
            return "build_bridge"
        
        # Déplacement
        if can_move and self.btn_move_army.handle_event(event):
            return "move_army"

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