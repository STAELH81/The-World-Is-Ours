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
        self.bridge_hp = 0
        self.discovered_by = set()
        self.capital_owner = Country.NONE
        self.city_owner = Country.NONE
        self.last_recruit_turn = -1
        
    def draw(self, surface, assets=None, show_units=True):
        screen_x = self.x * CELL_SIZE
        screen_y = self.y * CELL_SIZE
        
        color = TERRAIN_COLORS[self.terrain]
        terrain_sprite = assets.terrain.get(self.terrain) if assets else None
        
        if self.is_selected:
            color = tuple(min(255, c + 60) for c in color)

        if terrain_sprite:
            surface.blit(terrain_sprite, (screen_x, screen_y))
            if self.is_selected:
                # Keep selection readable above the terrain sprite.
                selection_overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                selection_overlay.fill((255, 255, 255, 45))
                surface.blit(selection_overlay, (screen_x, screen_y))
        else:
            pygame.draw.rect(surface, color, (screen_x, screen_y, CELL_SIZE, CELL_SIZE))
        
        if self.country != Country.NONE:
            border_overlay = assets.overlays.get(self.country) if assets else None
            if border_overlay:
                surface.blit(border_overlay, (screen_x, screen_y))
            else:
                border_color = COUNTRY_COLORS[self.country]
                pygame.draw.rect(surface, border_color, 
                               (screen_x, screen_y, CELL_SIZE, CELL_SIZE), 3)
        
        # Capitale
        if self.is_capital:
            center_x = screen_x + CELL_SIZE // 2
            center_y = screen_y + CELL_SIZE // 2
            capital_sprite = assets.buildings.get("capital") if assets else None
            if capital_sprite:
                sprite_rect = capital_sprite.get_rect(center=(center_x, center_y))
                surface.blit(capital_sprite, sprite_rect)
            else:
                pygame.draw.circle(surface, COUNTRY_COLORS[self.country], (center_x, center_y), 10)
                pygame.draw.circle(surface, (0, 0, 0), (center_x, center_y), 7)
            return
        
        # Ville
        if self.is_city:
            center_x = screen_x + CELL_SIZE // 2
            center_y = screen_y + CELL_SIZE // 2
            city_sprite = assets.buildings.get("city") if assets else None
            if city_sprite:
                sprite_rect = city_sprite.get_rect(center=(center_x, center_y))
                surface.blit(city_sprite, sprite_rect)
            else:
                # Carré pour la ville
                pygame.draw.rect(surface, COUNTRY_COLORS[self.country], 
                                (center_x - 8, center_y - 8, 16, 16))
                pygame.draw.rect(surface, (0, 0, 0), 
                                (center_x - 6, center_y - 6, 12, 12))
            return
        
        # Affiche l'armée si présente
        if show_units and self.army:
            self.draw_army(surface, screen_x, screen_y, assets)
    
    def draw_army(self, surface, screen_x, screen_y, assets=None):
        """Dessine l'armée sur la case"""
        # Fond semi-transparent
        army_bg = pygame.Surface((CELL_SIZE - 6, CELL_SIZE - 6), pygame.SRCALPHA)
        army_bg.fill((*COUNTRY_COLORS[self.army.country], 180))
        surface.blit(army_bg, (screen_x + 3, screen_y + 3))

        # Sprite unité (fallback emoji si absent)
        unit_sprite = assets.units.get(self.army.unit_type) if assets else None
        if unit_sprite:
            sprite_rect = unit_sprite.get_rect(center=(screen_x + CELL_SIZE // 2, screen_y + 12))
            surface.blit(unit_sprite, sprite_rect)
        else:
            font_symbol = pygame.font.Font(None, 20)
            symbol = font_symbol.render(UNIT_SYMBOLS[self.army.unit_type], True, (255, 255, 255))
            symbol_rect = symbol.get_rect(center=(screen_x + CELL_SIZE // 2, screen_y + 10))
            surface.blit(symbol, symbol_rect)
        
        # Nombre d'unités
        font_count = pygame.font.Font(None, 18)
        count_text = font_count.render(f"x{self.army.count}", True, (255, 255, 255))
        count_rect = count_text.get_rect(center=(screen_x + CELL_SIZE // 2, screen_y + CELL_SIZE - 8))
        surface.blit(count_text, count_rect)