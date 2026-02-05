import pygame
from constants import *

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.terrain = TerrainType.WATER
        self.country = Country.NONE
        self.is_selected = False
        self.is_capital = False
        self.is_city = False  # NOUVEAU
        self.army = None
        
    def draw(self, surface):
        screen_x = self.x * CELL_SIZE
        screen_y = self.y * CELL_SIZE
        
        color = TERRAIN_COLORS[self.terrain]
        
        if self.is_selected:
            color = tuple(min(255, c + 60) for c in color)
        
        pygame.draw.rect(surface, color, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))
        
        if self.country != Country.NONE:
            border_color = COUNTRY_COLORS[self.country]
            pygame.draw.rect(surface, border_color, 
                           (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 3)
        
        # Capitale
        if self.is_capital:
            center_x = screen_x + CELL_SIZE // 2
            center_y = screen_y + CELL_SIZE // 2
            pygame.draw.circle(surface, COUNTRY_COLORS[self.country], (center_x, center_y), 10)
            pygame.draw.circle(surface, (0, 0, 0), (center_x, center_y), 7)
            return
        
        # Ville
        if self.is_city:
            center_x = screen_x + CELL_SIZE // 2
            center_y = screen_y + CELL_SIZE // 2
            # Carré pour la ville
            pygame.draw.rect(surface, COUNTRY_COLORS[self.country], 
                            (center_x - 8, center_y - 8, 16, 16))
            pygame.draw.rect(surface, (0, 0, 0), 
                            (center_x - 6, center_y - 6, 12, 12))
            return
        
        # NOUVEAU : Affiche l'armée si présente
        if self.army:
            self.draw_army(surface, screen_x, screen_y)
    
    def draw_army(self, surface, screen_x, screen_y):
        """Dessine l'armée sur la case"""
        # Fond semi-transparent
        army_bg = pygame.Surface((CELL_SIZE - 6, CELL_SIZE - 6), pygame.SRCALPHA)
        army_bg.fill((*COUNTRY_COLORS[self.army.country], 180))
        surface.blit(army_bg, (screen_x + 3, screen_y + 3))
        
        # Symbole de l'unité
        font_symbol = pygame.font.Font(None, 20)
        symbol = font_symbol.render(UNIT_SYMBOLS[self.army.unit_type], True, (255, 255, 255))
        symbol_rect = symbol.get_rect(center=(screen_x + CELL_SIZE // 2, screen_y + 10))
        surface.blit(symbol, symbol_rect)
        
        # Nombre d'unités
        font_count = pygame.font.Font(None, 18)
        count_text = font_count.render(f"x{self.army.count}", True, (255, 255, 255))
        count_rect = count_text.get_rect(center=(screen_x + CELL_SIZE // 2, screen_y + CELL_SIZE - 8))
        surface.blit(count_text, count_rect)