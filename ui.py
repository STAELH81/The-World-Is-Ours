import pygame
from constants import *
from menu import Button


class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 28)
        self.font_normal = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        self.font_tiny = pygame.font.Font(None, 16)
        self.context_rect = pygame.Rect(0, 0, 0, 0)

        self.btn_end_turn = Button(WINDOW_WIDTH - 206, WINDOW_HEIGHT - 64, 194, 50, "Fin de tour", (39, 174, 96), (46, 204, 113))
        self.btn_research = Button(WINDOW_WIDTH - 248, 8, 236, 36, "Tech", (70, 90, 130), (90, 115, 160))
        self.btn_fortify = Button(0, 0, 120, 32, "Fortifier", (80, 110, 90), (96, 130, 108))
        self.btn_disembark = Button(0, 0, 140, 32, "Débarquer ici", (40, 110, 90), (55, 140, 110))
        self.btn_build_city = Button(0, 0, 200, 32, "Fonder une ville", (39, 174, 96), (46, 204, 113))
        self.btn_build_bridge = Button(0, 0, 160, 32, "Construire un pont", (127, 101, 65), (148, 122, 86))
        self.btn_recruit_swordsman = Button(0, 0, 130, 32, "Spadassin", (41, 128, 185), (52, 152, 219))
        self.btn_recruit_crossbowman = Button(0, 0, 140, 32, "Arbalétrier", (142, 68, 173), (155, 89, 182))
        self.btn_recruit_cavalry = Button(0, 0, 130, 32, "Cavalerie", (230, 126, 34), (243, 156, 18))

    def _place(self, button, x, y, w=None):
        if w is not None:
            button.rect.width = w
        button.rect.x = x
        button.rect.y = y
        return button.rect.right + 8

    def context(self, game):
        info = {
            "human": game.is_human_turn(),
            "cell": game.selected_cell,
            "player": game.players[game.get_ui_country()],
            "country": game.get_ui_country(),
            "army": None,
            "own_army": False,
            "can_fortify": False,
            "can_beach_land": False,
            "can_recruit": False,
            "already_recruited": False,
            "can_build_city": False,
            "can_build_bridge": False,
            "hint": "Clique une unité pour la déplacer, ou une ville pour recruter.",
        }
        cell = game.selected_cell
        if not cell:
            return info
        player = info["player"]
        own_tile = cell.country == info["country"]
        if cell.army:
            info["army"] = cell.army
            info["own_army"] = cell.army.country == info["country"]
        if info["own_army"] and info["human"] and cell.army.movement_left > 0:
            if not cell.army.embarked:
                info["can_fortify"] = True
            if cell.army.embarked and cell.terrain == TerrainType.BEACH:
                info["can_beach_land"] = True
        urban = own_tile and (cell.is_city or cell.is_capital)
        waterish = cell.terrain in (TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE)
        if urban and not waterish:
            info["already_recruited"] = cell.last_recruit_turn == game.turn_number
            info["can_recruit"] = info["human"] and not info["already_recruited"]
        if (
            info["human"]
            and own_tile
            and not info["own_army"]
            and not cell.is_city
            and not cell.is_capital
            and not cell.army
            and not waterish
        ):
            info["can_build_city"] = True
        if (
            info["human"]
            and own_tile
            and not info["own_army"]
            and not urban
            and game.cell_has_adjacent_water(cell)
        ):
            info["can_build_bridge"] = True
        if info["own_army"]:
            bits = []
            if cell.army.embarked:
                bits.append("Vert : débarquer")
            else:
                bits.append("Bleu : avancer")
                bits.append("Rouge : attaquer")
                if cell.army.unit_type == UnitType.CROSSBOWMAN:
                    bits.append("Violet : tirer")
                if game.get_embark_targets(cell):
                    bits.append("Cyan : embarquer")
            info["hint"] = "  ·  ".join(bits)
        elif info["can_recruit"]:
            info["hint"] = "Choisis une unité à recruter dans cette ville."
        elif info["already_recruited"]:
            info["hint"] = "Cette ville a déjà produit ce tour."
        elif info["can_build_city"]:
            info["hint"] = "Case libre : tu peux fonder une ville."
        else:
            info["hint"] = f"{TERRAIN_FULL_NAMES[cell.terrain]}  ·  {COUNTRY_NAMES[cell.country]}"
        return info

    def layout(self, game):
        ctx = self.context(game)
        player = ctx["player"]
        next_tech = player.get_next_tech()
        if next_tech:
            self.btn_research.text = f"{next_tech['name']}  {next_tech['cost']}"
        else:
            self.btn_research.text = "Techs terminées"
        self.btn_research.rect.x = WINDOW_WIDTH - 218
        self.btn_research.rect.y = 8
        self.btn_research.rect.width = 210

        idle = game.count_idle_armies(ctx["country"]) if ctx["human"] else 0
        if not ctx["human"]:
            self.btn_end_turn.text = "IA en cours..."
        elif idle:
            self.btn_end_turn.text = f"Fin de tour ({idle})"
        else:
            self.btn_end_turn.text = "Fin de tour"

        buttons = []
        if ctx["can_fortify"]:
            buttons.append(self.btn_fortify)
        if ctx["can_beach_land"]:
            buttons.append(self.btn_disembark)
        if ctx["can_recruit"]:
            self.btn_recruit_swordsman.text = f"Spadassin  {player.unit_cost(UnitType.SWORDSMAN)}"
            self.btn_recruit_crossbowman.text = f"Arbalétrier  {player.unit_cost(UnitType.CROSSBOWMAN)}"
            self.btn_recruit_cavalry.text = f"Cavalerie  {player.unit_cost(UnitType.CAVALRY)}"
            buttons.extend(
                [self.btn_recruit_swordsman, self.btn_recruit_crossbowman, self.btn_recruit_cavalry]
            )
        if ctx["can_build_city"]:
            self.btn_build_city.text = f"Fonder une ville  {CITY_COST}"
            buttons.append(self.btn_build_city)
        if ctx["can_build_bridge"]:
            self.btn_build_bridge.text = f"Pont  {player.bridge_cost()}"
            buttons.append(self.btn_build_bridge)

        extra = 36 if len(buttons) > 3 else 0
        if not ctx["cell"]:
            panel_h = 54
        else:
            panel_h = 88 + extra
        panel_w = min(460, WINDOW_WIDTH - 226)
        self.context_rect = pygame.Rect(10, WINDOW_HEIGHT - panel_h - 10, panel_w, panel_h)
        x = self.context_rect.x + 12
        y = self.context_rect.bottom - 42
        for button in buttons:
            width = max(118, self.font_small.size(button.text)[0] + 18)
            if x + width > self.context_rect.right - 8:
                x = self.context_rect.x + 12
                y -= 36
            x = self._place(button, x, y, width)
        return ctx, buttons

    def blocks_map(self, pos):
        if pos[1] < HUD_TOP:
            return True
        if self.context_rect.width and self.context_rect.collidepoint(pos):
            return True
        if self.btn_end_turn.rect.collidepoint(pos):
            return True
        return False

    def draw(self, game):
        ctx, buttons = self.layout(game)
        self._draw_city_banners(game)
        self._draw_top_bar(game, ctx)
        self._draw_event_log(game)
        self._draw_context_panel(game, ctx, buttons)
        self.btn_end_turn.draw(self.screen, self.font_normal)

    def _draw_top_bar(self, game, ctx):
        pygame.draw.rect(self.screen, (18, 20, 26), (0, 0, WINDOW_WIDTH, HUD_TOP))
        pygame.draw.line(self.screen, (70, 74, 84), (0, HUD_TOP - 1), (WINDOW_WIDTH, HUD_TOP - 1), 1)
        country = ctx["country"]
        player = ctx["player"]
        pygame.draw.circle(self.screen, COUNTRY_COLORS[country], (16, HUD_TOP // 2), 8)
        name = COUNTRY_NAMES[country]
        self.screen.blit(self.font_small.render(name, True, (235, 235, 235)), (28, 6))
        trait = player.trait_info()
        if trait:
            self.screen.blit(self.font_tiny.render(trait["name"], True, (200, 190, 140)), (28, 28))

        gold = self.font_normal.render(f"{player.gold}", True, (255, 210, 80))
        self.screen.blit(gold, (168, 6))
        self.screen.blit(self.font_tiny.render("or", True, (255, 210, 80)), (168 + gold.get_width() + 4, 10))
        yield_line = self.font_tiny.render(
            f"+{game.last_income}  -{game.last_upkeep}", True, (170, 185, 170)
        )
        self.screen.blit(yield_line, (168, 28))

        active = game.current_player_country
        status = f"Tour {game.turn_number}"
        if game.game_mode == "solo" and active != country:
            status += "  IA"
        elif getattr(game, "fx", None) and game.fx.is_busy():
            status += "  …"
        self.screen.blit(self.font_small.render(status, True, (220, 220, 225)), (268, 16))
        self.btn_research.rect.width = 210
        self.btn_research.rect.x = WINDOW_WIDTH - 218
        self.btn_research.rect.y = 8
        self.btn_research.draw(self.screen, self.font_small)

    def _draw_city_banners(self, game):
        viewer = game.get_viewer_country()
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = game.grid[x][y]
                if not (cell.is_capital or cell.is_city):
                    continue
                if (x, y) not in game.visibility and viewer not in cell.discovered_by:
                    continue
                sx, sy = cell_screen_pos(x, y)
                label = "Capitale" if cell.is_capital else "Ville"
                color = COUNTRY_COLORS.get(cell.country, (200, 200, 200))
                surf = self.font_tiny.render(label, True, (20, 20, 24))
                pad = 4
                rect = pygame.Rect(0, 0, surf.get_width() + pad * 2, surf.get_height() + 2)
                rect.midbottom = (sx + CELL_SIZE // 2, sy - 1)
                if rect.top < HUD_TOP:
                    rect.top = sy + CELL_SIZE + 1
                pygame.draw.rect(self.screen, color, rect, border_radius=3)
                self.screen.blit(surf, (rect.x + pad, rect.y + 1))

    def _draw_event_log(self, game):
        y = HUD_TOP + 8
        for msg in game.event_log[-3:]:
            text = self.font_tiny.render(msg[:54], True, (230, 230, 230))
            bg = pygame.Surface((text.get_width() + 10, text.get_height() + 4), pygame.SRCALPHA)
            bg.fill((10, 12, 16, 160))
            self.screen.blit(bg, (8, y))
            self.screen.blit(text, (13, y + 2))
            y += 18

    def _draw_context_panel(self, game, ctx, buttons):
        pygame.draw.rect(self.screen, (22, 24, 32), self.context_rect, border_radius=10)
        pygame.draw.rect(self.screen, (80, 86, 98), self.context_rect, 1, border_radius=10)
        x = self.context_rect.x + 12
        y = self.context_rect.y + 8
        cell = ctx["cell"]
        if ctx["army"]:
            army = ctx["army"]
            ship = "  navire" if army.embarked else ""
            title = f"{UNIT_NAMES[army.unit_type]}{ship}  ×{army.count}"
            self.screen.blit(self.font_normal.render(title, True, (255, 230, 140)), (x, y))
            pm = f"PM {army.movement_left}/{army.movement_range(game.players.get(army.country))}"
            self.screen.blit(self.font_small.render(pm, True, (200, 200, 205)), (x + 250, y + 4))
        elif cell and (cell.is_capital or cell.is_city):
            kind = "Capitale" if cell.is_capital else "Ville"
            self.screen.blit(self.font_normal.render(kind, True, (255, 230, 140)), (x, y))
        elif cell:
            self.screen.blit(
                self.font_normal.render(TERRAIN_FULL_NAMES[cell.terrain], True, (230, 230, 230)),
                (x, y),
            )
        else:
            self.screen.blit(self.font_normal.render("Aucune sélection", True, (200, 200, 205)), (x, y))
        self.screen.blit(self.font_tiny.render(ctx["hint"], True, (170, 175, 185)), (x, y + 24))
        if ctx["already_recruited"] and not ctx["can_recruit"]:
            self.screen.blit(
                self.font_tiny.render("Production déjà utilisée", True, (180, 140, 140)),
                (x, y + 40),
            )
        for button in buttons:
            button.draw(self.screen, self.font_small)

    def handle_event(self, event, game):
        ctx, buttons = self.layout(game)
        if self.btn_end_turn.handle_event(event):
            return "end_turn"
        if ctx["human"] and self.btn_research.handle_event(event):
            return "research_next"

        visible = set(id(button) for button in buttons)
        if ctx["can_fortify"] and id(self.btn_fortify) in visible and self.btn_fortify.handle_event(event):
            return "fortify"
        if ctx["can_beach_land"] and self.btn_disembark.handle_event(event):
            return "disembark_mode"
        if ctx["can_build_city"] and self.btn_build_city.handle_event(event):
            return "build_city"
        if ctx["can_build_bridge"] and self.btn_build_bridge.handle_event(event):
            return "build_bridge"
        if ctx["can_recruit"]:
            if self.btn_recruit_swordsman.handle_event(event):
                return ("recruit", UnitType.SWORDSMAN)
            if self.btn_recruit_crossbowman.handle_event(event):
                return ("recruit", UnitType.CROSSBOWMAN)
            if self.btn_recruit_cavalry.handle_event(event):
                return ("recruit", UnitType.CAVALRY)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.blocks_map(event.pos):
            return "hud_click"
        return None
