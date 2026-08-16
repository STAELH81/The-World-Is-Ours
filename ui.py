import pygame
from constants import *
from menu import Button
from theme import (
    CREAM,
    GOLD,
    GOLD_BRIGHT,
    INK,
    INK_SOFT,
    PARCHMENT,
    WOOD,
    WOOD_DARK,
    WOOD_LIGHT,
    blit_outlined,
    draw_bevel_rect,
    load_font,
)


class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = load_font(24, bold=True)
        self.font_normal = load_font(20, bold=True)
        self.font_small = load_font(18)
        self.font_tiny = load_font(16)
        self.context_rect = pygame.Rect(0, 0, 0, 0)
        self.btn_end_turn = Button(WINDOW_WIDTH - 214, WINDOW_HEIGHT - 62, 202, 48, "Fin de tour")
        self.btn_research = Button(WINDOW_WIDTH - 250, 8, 238, 28, "Tech")
        self.btn_fortify = Button(0, 0, 120, 34, "Fortifier")
        self.btn_disembark = Button(0, 0, 140, 34, "Débarquer ici")
        self.btn_build_city = Button(0, 0, 200, 34, "Fonder une ville")
        self.btn_build_bridge = Button(0, 0, 160, 34, "Pont")
        self.btn_recruit_swordsman = Button(0, 0, 130, 34, "Spadassin")
        self.btn_recruit_spearman = Button(0, 0, 120, 34, "Lancier")
        self.btn_recruit_crossbowman = Button(0, 0, 140, 34, "Arbalétrier")
        self.btn_recruit_cavalry = Button(0, 0, 130, 34, "Cavalerie")
        self.btn_recruit_catapult = Button(0, 0, 130, 34, "Catapulte")

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
            "idle": 0,
            "hint": "N : unité suivante. Clique une ville pour produire.",
        }
        cell = game.selected_cell
        info["idle"] = game.count_idle_armies(info["country"]) if info["human"] else 0
        if not cell:
            return info
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
            and game.has_adjacent_bridge_site(cell)
        ):
            info["can_build_bridge"] = True
        if info["own_army"]:
            name = UNIT_NAMES[cell.army.unit_type]
            if cell.army.embarked:
                info["hint"] = f"{name} en mer. Clique une plage ou une terre pour débarquer."
            else:
                info["hint"] = f"{name}. Les cases vertes sont ta portée. Survole pour voir l'arrêt."
        elif info["can_recruit"]:
            info["hint"] = "Cette ville peut produire une unité ce tour."
        elif info["already_recruited"]:
            info["hint"] = "Cette ville a déjà produit ce tour."
        elif info["can_build_city"]:
            info["hint"] = "Case libre : tu peux fonder une ville."
        else:
            owner = COUNTRY_SHORT.get(cell.country) or "Neutre"
            info["hint"] = f"{TERRAIN_FULL_NAMES[cell.terrain]}, {owner}"
        return info

    def layout(self, game):
        ctx = self.context(game)
        player = ctx["player"]
        next_tech = player.get_next_tech()
        if next_tech:
            self.btn_research.text = f"{next_tech['name']}  {next_tech['cost']} or"
        else:
            self.btn_research.text = "Techs terminées"
        self.btn_research.rect.x = WINDOW_WIDTH - 246
        self.btn_research.rect.y = 6
        self.btn_research.rect.width = 234
        self.btn_research.rect.height = 28

        idle = ctx["idle"]
        if not ctx["human"]:
            self.btn_end_turn.text = "Tour de l'IA…"
            self.btn_end_turn.color = WOOD
        elif idle:
            self.btn_end_turn.text = f"Unité suivante  ({idle})"
            self.btn_end_turn.color = WOOD
            self.btn_end_turn.hover_color = WOOD_LIGHT
        else:
            pulse = (pygame.time.get_ticks() // 420) % 2 == 0
            self.btn_end_turn.text = "Fin de tour"
            self.btn_end_turn.color = (140, 92, 28) if pulse else WOOD_LIGHT
            self.btn_end_turn.hover_color = GOLD

        buttons = []
        if ctx["can_fortify"]:
            buttons.append(self.btn_fortify)
        if ctx["can_beach_land"]:
            buttons.append(self.btn_disembark)
        if ctx["can_recruit"]:
            self.btn_recruit_swordsman.text = f"Spada  {player.unit_cost(UnitType.SWORDSMAN)}"
            self.btn_recruit_spearman.text = f"Lancier  {player.unit_cost(UnitType.SPEARMAN)}"
            self.btn_recruit_crossbowman.text = f"Arbalète  {player.unit_cost(UnitType.CROSSBOWMAN)}"
            self.btn_recruit_cavalry.text = f"Caval.  {player.unit_cost(UnitType.CAVALRY)}"
            self.btn_recruit_catapult.text = f"Catap.  {player.unit_cost(UnitType.CATAPULT)}"
            buttons.extend(
                [
                    self.btn_recruit_swordsman,
                    self.btn_recruit_spearman,
                    self.btn_recruit_crossbowman,
                    self.btn_recruit_cavalry,
                    self.btn_recruit_catapult,
                ]
            )
        if ctx["can_build_city"]:
            self.btn_build_city.text = f"Fonder une ville  {CITY_COST}"
            buttons.append(self.btn_build_city)
        if ctx["can_build_bridge"]:
            self.btn_build_bridge.text = f"Pont  {player.bridge_cost()}"
            buttons.append(self.btn_build_bridge)

        extra = 38 if len(buttons) > 3 else 0
        panel_h = 58 if not ctx["cell"] else 96 + extra
        panel_w = min(620, WINDOW_WIDTH - 230)
        self.context_rect = pygame.Rect(8, WINDOW_HEIGHT - panel_h - 8, panel_w, panel_h)
        x = self.context_rect.x + 14
        y = self.context_rect.bottom - 44
        for button in buttons:
            width = max(128, self.font_small.size(button.text)[0] + 20)
            if x + width > self.context_rect.right - 8:
                x = self.context_rect.x + 14
                y -= 38
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
        bar = pygame.Rect(0, 0, WINDOW_WIDTH, HUD_TOP)
        draw_bevel_rect(self.screen, bar, WOOD, GOLD_BRIGHT, WOOD_DARK, 2)
        pygame.draw.line(self.screen, GOLD, (0, HUD_TOP - 2), (WINDOW_WIDTH, HUD_TOP - 2), 2)
        country = ctx["country"]
        player = ctx["player"]
        pygame.draw.circle(self.screen, COUNTRY_COLORS[country], (18, 22), 9)
        pygame.draw.circle(self.screen, GOLD, (18, 22), 9, 1)
        self.screen.blit(self.font_normal.render(COUNTRY_SHORT[country], True, CREAM), (32, 6))
        trait = player.trait_info()
        if trait:
            self.screen.blit(self.font_tiny.render(trait["name"], True, GOLD_BRIGHT), (32, 30))

        gold = self.font_title.render(str(player.gold), True, GOLD_BRIGHT)
        self.screen.blit(gold, (200, 4))
        self.screen.blit(self.font_tiny.render("or", True, GOLD), (200 + gold.get_width() + 6, 10))
        self.screen.blit(
            self.font_tiny.render(f"+{game.last_income}  -{game.last_upkeep}", True, PARCHMENT),
            (200, 32),
        )

        active = game.current_player_country
        status = f"Tour {game.turn_number}"
        if game.game_mode == "solo" and active != country:
            status += "  (IA)"
        self.screen.blit(self.font_small.render(status, True, CREAM), (400, 8))
        self.screen.blit(self.font_tiny.render("N unité suivante    Espace fin de tour    Échap pause", True, PARCHMENT), (400, 30))
        self.btn_research.draw(self.screen, self.font_tiny)

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
                name = COUNTRY_SHORT.get(cell.country, "?")
                label = name
                surf = self.font_tiny.render(label, True, CREAM)
                pos = (sx + (CELL_SIZE - surf.get_width()) // 2, sy - 16)
                if pos[1] < HUD_TOP:
                    pos = (pos[0], sy + CELL_SIZE + 1)
                blit_outlined(self.screen, self.font_tiny, label, CREAM, (20, 12, 8), pos)

    def _draw_event_log(self, game):
        y = HUD_TOP + 6
        for msg in game.event_log[-3:]:
            blit_outlined(self.screen, self.font_tiny, msg[:60], CREAM, (20, 12, 8), (10, y))
            y += 18

    def _draw_context_panel(self, game, ctx, buttons):
        draw_bevel_rect(self.screen, self.context_rect, WOOD, GOLD_BRIGHT, WOOD_DARK, 2)
        inner = self.context_rect.inflate(-6, -6)
        pygame.draw.rect(self.screen, PARCHMENT, inner)
        pygame.draw.rect(self.screen, GOLD, inner, 1)
        x = self.context_rect.x + 14
        y = self.context_rect.y + 8
        cell = ctx["cell"]
        if ctx["army"]:
            army = ctx["army"]
            ship = " en mer" if army.embarked else ""
            title = f"{UNIT_NAMES[army.unit_type]}{ship}  x{army.count}"
            self.screen.blit(self.font_normal.render(title, True, INK), (x, y))
            pm = f"mouvement {army.movement_left}/{army.movement_range(game.players.get(army.country))}"
            self.screen.blit(self.font_small.render(pm, True, INK_SOFT), (x + 268, y + 2))
        elif cell and (cell.is_capital or cell.is_city):
            kind = "Capitale" if cell.is_capital else "Ville"
            self.screen.blit(self.font_normal.render(kind, True, INK), (x, y))
        elif cell:
            self.screen.blit(
                self.font_normal.render(TERRAIN_FULL_NAMES[cell.terrain], True, INK),
                (x, y),
            )
        else:
            self.screen.blit(self.font_normal.render("Aucune sélection", True, INK_SOFT), (x, y))
        self.screen.blit(self.font_tiny.render(ctx["hint"], True, INK_SOFT), (x, y + 26))
        if ctx["already_recruited"] and not ctx["can_recruit"]:
            self.screen.blit(
                self.font_tiny.render("Production déjà utilisée", True, (140, 48, 36)),
                (x, y + 44),
            )
        for button in buttons:
            button.draw(self.screen, self.font_small)

    def handle_event(self, event, game):
        ctx, buttons = self.layout(game)
        if self.btn_end_turn.handle_event(event):
            if ctx["human"] and ctx["idle"]:
                return "next_unit"
            return "end_turn"
        if ctx["human"] and self.btn_research.handle_event(event):
            return "research_next"
        if ctx["can_fortify"] and self.btn_fortify.handle_event(event):
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
            if self.btn_recruit_spearman.handle_event(event):
                return ("recruit", UnitType.SPEARMAN)
            if self.btn_recruit_crossbowman.handle_event(event):
                return ("recruit", UnitType.CROSSBOWMAN)
            if self.btn_recruit_cavalry.handle_event(event):
                return ("recruit", UnitType.CAVALRY)
            if self.btn_recruit_catapult.handle_event(event):
                return ("recruit", UnitType.CATAPULT)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.blocks_map(event.pos):
            return "hud_click"
        return None
