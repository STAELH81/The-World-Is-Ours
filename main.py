import pygame
import sys
from constants import *
from cell import Cell
from ui import UI

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("The World Is Ours")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Grille de cellules
        self.grid = [[Cell(x, y) for y in range(GRID_ROWS)] for x in range(GRID_COLS)]
        
        # Cellule sélectionnée
        self.selected_cell = None

        # UI
        self.ui = UI(self.screen)
        
        # Génère la map
        self.generate_map()
    
    def place_capitals(self):
        # Rouge - Île 1 (nord-ouest de l'île)
        self.grid[3][3].is_capital = True
        # Vert - Île 1 (sud-est de l'île)
        self.grid[7][8].is_capital = True
        # Bleu - Île 2
        self.grid[14][4].is_capital = True
        # Jaune - Île 3
        self.grid[4][23].is_capital = True
        # Orange - Île 4
        self.grid[14][21].is_capital = True   
        # Génère les capitales

    def generate_map(self):
        # Île 1 - Nord-Ouest (Rouge + Vert)
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
        
        # Île 2 - Nord-Est (Bleu)
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
        
        # Île 3 - Sud-Ouest (Jaune)
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
        
        # Île 4 - Sud-Est (Orange)
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
        
        # Île 5 - Petite île centrale (Rouge)
        ile5 = [
            (8,14), (9,14), (10,14),
            (7,15), (8,15), (9,15), (10,15), (11,15),
            (7,16), (8,16), (9,16), (10,16), (11,16),
            (8,17), (9,17), (10,17), (11,17),
            (9,18), (10,18), (11,18),
        ]
        
        # Applique les terrains
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
        
        # Applique les pays
        self.apply_country(rouge, Country.RED)
        self.apply_country(vert, Country.GREEN)
        self.apply_country(ile2, Country.BLUE)
        self.apply_country(ile3, Country.YELLOW)
        self.apply_country(ile4, Country.ORANGE)
        self.apply_country(ile5, Country.RED)
        
        # Génère les plages
        self.add_beaches()
        self.place_capitals()     
    
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
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Clic gauche
                x, y = event.pos
                cell_x = x // CELL_SIZE
                cell_y = y // CELL_SIZE
                
                if 0 <= cell_x < GRID_COLS and 0 <= cell_y < GRID_ROWS:
                    # Désélectionne l'ancienne
                    if self.selected_cell:
                        self.selected_cell.is_selected = False
                    
                    # Sélectionne la nouvelle
                    self.selected_cell = self.grid[cell_x][cell_y]
                    self.selected_cell.is_selected = True
                    
                    print(f"Case ({cell_x}, {cell_y}) - Terrain: {self.selected_cell.terrain.name} - Pays: {self.selected_cell.country.name}")
    
    def update(self):
        pass
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        
        # Dessine toutes les cellules
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                self.grid[x][y].draw(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            # Dessine l'UI
            self.ui.draw(self)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()