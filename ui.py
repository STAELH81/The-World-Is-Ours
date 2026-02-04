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
        y_offset += 50
        
        # Pays actuellement joué (pour l'instant on met Rouge par défaut)
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
        y_offset += 40
        
        # Or (placeholder pour l'instant)
        gold = player.gold
        text = self.font_normal.render(f"Or: {gold}", True, (255, 215, 0))
        self.screen.blit(text, (self.panel_x + 30, y_offset))
        y_offset += 50
        
        # Infos case sélectionnée
        if game.selected_cell:
            self.draw_section_title("Case sélectionnée", y_offset)
            y_offset += 30
            
            cell = game.selected_cell
            
            # Position
            text = self.font_small.render(f"Position: ({cell.x}, {cell.y})", True, UI_TEXT_COLOR)
            self.screen.blit(text, (self.panel_x + 30, y_offset))
            y_offset += 25
            
            # Terrain
            terrain_name = TERRAIN_FULL_NAMES[cell.terrain]
            text = self.font_small.render(f"Terrain: {terrain_name}", True, UI_TEXT_COLOR)
            self.screen.blit(text, (self.panel_x + 30, y_offset))
            y_offset += 25
            
            # Pays
            if cell.country != Country.NONE:
                country_name = COUNTRY_NAMES[cell.country]
                pygame.draw.circle(self.screen, COUNTRY_COLORS[cell.country], 
                                 (self.panel_x + 40, y_offset + 8), 6)
                text = self.font_small.render(country_name, True, UI_TEXT_COLOR)
                self.screen.blit(text, (self.panel_x + 55, y_offset))
                y_offset += 25
            else:
                text = self.font_small.render("Pays: Neutre", True, UI_TEXT_COLOR)
                self.screen.blit(text, (self.panel_x + 30, y_offset))
                y_offset += 25
            
            # Capitale
            if cell.is_capital:
                text = self.font_small.render("⭐ Capitale", True, (255, 215, 0))
                self.screen.blit(text, (self.panel_x + 30, y_offset))
                y_offset += 25

            # Armée
            if cell.army:
                y_offset += 10
                army_name = UNIT_NAMES[cell.army.unit_type]
                symbol = UNIT_SYMBOLS[cell.army.unit_type]
                text = self.font_small.render(f"{symbol} {army_name} x{cell.army.count}", True, (255, 255, 100))
                self.screen.blit(text, (self.panel_x + 30, y_offset))
                y_offset += 25

        # Stats globales
        y_offset = WINDOW_HEIGHT - 150
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
                y_offset += 22

        # Bouton fin de tour
        self.btn_end_turn.draw(self.screen, self.font_normal)

        # Numéro de tour
        turn_text = self.font_small.render(f"Tour: {game.turn_number}", True, UI_TEXT_COLOR)
        self.screen.blit(turn_text, (self.panel_x + 20, WINDOW_HEIGHT - 120))
    
    def handle_event(self, event):
        """Gère les événements UI"""
        if self.btn_end_turn.handle_event(event):
            return "end_turn"
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