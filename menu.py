import pygame
from constants import *

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=8)
        
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                return True
        return False

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # État du menu
        self.state = "main"  # main, mode_select
        self.selected_mode = None
        
        # Boutons menu principal
        button_width = 300
        button_height = 60
        button_x = (WINDOW_WIDTH - button_width) // 2
        start_y = 300
        
        self.btn_new_game = Button(
            button_x, start_y, button_width, button_height,
            "Nouvelle Partie", (41, 128, 185), (52, 152, 219)
        )
        
        self.btn_load_game = Button(
            button_x, start_y + 80, button_width, button_height,
            "Charger Partie", (39, 174, 96), (46, 204, 113)
        )
        
        self.btn_quit = Button(
            button_x, start_y + 160, button_width, button_height,
            "Quitter", (192, 57, 43), (231, 76, 60)
        )
        
        # Boutons sélection de mode
        self.btn_solo = Button(
            button_x, start_y, button_width, button_height,
            "Solo (vs IA)", (142, 68, 173), (155, 89, 182)
        )
        
        self.btn_godgame = Button(
            button_x, start_y + 80, button_width, button_height,
            "God Game", (230, 126, 34), (243, 156, 18)
        )
        
        self.btn_back = Button(
            button_x, start_y + 160, button_width, button_height,
            "Retour", (127, 140, 141), (149, 165, 166)
        )
    
    def handle_event(self, event):
        if self.state == "main":
            if self.btn_new_game.handle_event(event):
                self.state = "mode_select"
                return None
            
            if self.btn_load_game.handle_event(event):
                return "load"
            
            if self.btn_quit.handle_event(event):
                return "quit"
        
        elif self.state == "mode_select":
            if self.btn_solo.handle_event(event):
                return "start_solo"
            
            if self.btn_godgame.handle_event(event):
                return "start_godgame"
            
            if self.btn_back.handle_event(event):
                self.state = "main"
                return None
        
        return None
    
    def draw(self):
        # Fond
        self.screen.fill((30, 30, 35))
        
        # Titre
        title = self.font_title.render("The World Is Ours", True, (255, 215, 0))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Sous-titre
        if self.state == "main":
            subtitle = self.font_small.render("Un jeu de conquête médiéval", True, (200, 200, 200))
        else:
            subtitle = self.font_small.render("Choisissez votre mode de jeu", True, (200, 200, 200))
        
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 220))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Dessine les boutons selon l'état
        if self.state == "main":
            self.btn_new_game.draw(self.screen, self.font_button)
            self.btn_load_game.draw(self.screen, self.font_button)
            self.btn_quit.draw(self.screen, self.font_button)
        
        elif self.state == "mode_select":
            self.btn_solo.draw(self.screen, self.font_button)
            self.btn_godgame.draw(self.screen, self.font_button)
            self.btn_back.draw(self.screen, self.font_button)
            
            # Descriptions des modes
            y = 550
            solo_desc = self.font_small.render("Jouez contre l'ordinateur", True, (180, 180, 180))
            god_desc = self.font_small.render("Contrôlez tous les pays", True, (180, 180, 180))
            
            solo_rect = solo_desc.get_rect(center=(WINDOW_WIDTH // 2, y))
            god_rect = god_desc.get_rect(center=(WINDOW_WIDTH // 2, y + 80))
            
            if self.btn_solo.is_hovered:
                self.screen.blit(solo_desc, solo_rect)
            elif self.btn_godgame.is_hovered:
                self.screen.blit(god_desc, god_rect)
        
        pygame.display.flip()