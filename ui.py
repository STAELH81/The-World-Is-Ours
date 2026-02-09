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
        
        # Boutons de recrutement
        recruit_y = 500
        button_small_width = 250
        button_small_height = 40
        spacing = 10

        self.btn_recruit_swordsman = Button(
            self.panel_x + 25,
            recruit_y,
            button_small_width,
            button_small_height,
            f"⚔ Spadassin ({UNIT_COSTS[UnitType.SWORDSMAN]} or)",
            (41, 128, 185),
            (52, 152, 219)
        )

        self.btn_recruit_crossbowman = Button(
            self.panel_x + 25,
            recruit_y + button_small_height + spacing,
            button_small_width,
            button_small_height,
            f"🏹 Arbalétrier ({UNIT_COSTS[UnitType.CROSSBOWMAN]} or)",
            (142, 68, 173),
            (155, 89, 182)
        )

        self.btn_recruit_cavalry = Button(
            self.panel_x + 25,
            recruit_y + (button_small_height + spacing) * 2,
            button_small_width,
            button_small_height,
            f"🐴 Cavalerie ({UNIT_COSTS[UnitType.CAVALRY]} or)",
            (230, 126, 34),
            (243, 156, 18)
        )

        # Bouton construction ville
        self.btn_build_city = Button(
            self.panel_x + 25,
            recruit_y + (button_small_height + spacing) * 3,
            button_small_width,
            button_small_height,
            f"🏘 Construire ville (150 or)",
            (39, 174, 96),
            (46, 204, 113)
        )

        # Bouton déplacement
        self.btn_move_army = Button(
            self.panel_x + 25,
            recruit_y + (button_small_height + spacing) * 4,
            button_small_width,
            button_small_height,
            f"➡️ Déplacer armée",
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

        # Titre
        title = self.font_title.render("The World Is Ours", True, UI_TITLE_COLOR)
        self.screen.blit(title, (self.panel_x + 20, y_offset))
        y_offset += 40

        # Numéro de tour
        turn_text = self.font_small.render(f"Tour: {game.turn_number}", True, (150, 150, 150))
        self.screen.blit(turn_text, (self.panel_x + 20, y_offset))
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

            y_offset += 20

        # Stats globales
        self.draw_section_title("Statistiques", y_offset)
        y_offset += 30

        # Compte les territoires par pays
        territories = self.count_territories(game)
        for country, count in territories.items():
            if country != Country.NONE and count > 0:
                pygame.draw.circle(self.screen, COUNTRY_COLORS[country], 
                                 (self.panel_x + 30, y_offset + 8), 6)
                text = self.font_small.render(f"{count} cases", True, UI_TEXT_COLOR)
                self.screen.blit(text, (self.panel_x + 45, y_offset))
                y_offset += 20

        # Section recrutement
        recruit_y = WINDOW_HEIGHT - 260
        self.draw_section_title("Recrutement", recruit_y)
        recruit_y += 35

        # Affiche les boutons seulement si une case du joueur est sélectionnée
        if game.selected_cell and game.selected_cell.country == current_country:
            self.btn_recruit_swordsman.draw(self.screen, self.font_small)
            self.btn_recruit_crossbowman.draw(self.screen, self.font_small)
            self.btn_recruit_cavalry.draw(self.screen, self.font_small)
            self.btn_build_city.draw(self.screen, self.font_small)
            
            # Bouton déplacement seulement si armée présente
            if game.selected_cell.army:
                self.btn_move_army.draw(self.screen, self.font_small)
        else:
            # Message si pas de case sélectionnée
            msg = self.font_small.render("Sélectionnez une", True, (150, 150, 150))
            msg2 = self.font_small.render("case pour recruter", True, (150, 150, 150))
            self.screen.blit(msg, (self.panel_x + 60, recruit_y + 30))
            self.screen.blit(msg2, (self.panel_x + 50, recruit_y + 50))

        # Bouton fin de tour
        self.btn_end_turn.draw(self.screen, self.font_normal)
    
    def handle_event(self, event):
        """Gère les événements UI"""
        if self.btn_end_turn.handle_event(event):
            return "end_turn"
        
        # Construction ville
        if self.btn_build_city.handle_event(event):
            return "build_city"
        
        # Déplacement
        if self.btn_move_army.handle_event(event):
            return "move_army"

        # Recrutement
        if self.btn_recruit_swordsman.handle_event(event):
            return ("recruit", UnitType.SWORDSMAN)
        if self.btn_recruit_crossbowman.handle_event(event):
            return ("recruit", UnitType.CROSSBOWMAN)
        if self.btn_recruit_cavalry.handle_event(event):
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