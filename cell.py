import pygame
from constants import *

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.terrain = TerrainType.WATER
        self.country = Country.NONE
        self.is_selected = False
        self.is_capital = False  # NOUVEAU
        
    def draw(self, surface):
        # Position sur l'écran
        screen_x = self.x * CELL_SIZE
        screen_y = self.y * CELL_SIZE
        
        # Couleur du terrain
        color = TERRAIN_COLORS[self.terrain]
        
        # Si sélectionné, éclaircir
        if self.is_selected:
            color = tuple(min(255, c + 60) for c in color)
        
        # Dessine la case
        pygame.draw.rect(surface, color, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))
        
        # Bordure pays
        if self.country != Country.NONE:
            border_color = COUNTRY_COLORS[self.country]
            pygame.draw.rect(surface, border_color, 
                           (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 3)
        
        # NOUVEAU : Dessine la capitale (cercle noir avec bord pays)
        if self.is_capital:
            center_x = screen_x + CELL_SIZE // 2
            center_y = screen_y + CELL_SIZE // 2
            # Cercle extérieur (couleur du pays)
            pygame.draw.circle(surface, COUNTRY_COLORS[self.country], (center_x, center_y), 10)
            # Cercle intérieur (noir)
            pygame.draw.circle(surface, (0, 0, 0), (center_x, center_y), 7)
            return  # Skip le texte terrain si c'est une capitale