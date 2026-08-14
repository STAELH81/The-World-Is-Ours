import pygame
from constants import *
from menu import Button


class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 28)
        self.font_normal = pygame.font.Font(None, 22)
        self.font_small = pygame.font.Font(None, 18)
        self.panel_x = GRID_COLS * CELL_SIZE
        self.panel_y = 0
        self.panel_width = UI_WIDTH
        self.panel_height = WINDOW_HEIGHT

        self.btn_end_turn = Button(
            self.panel_x + (UI_WIDTH - 200) // 2,
            WINDOW_HEIGHT - 80,
            200,
            50,
            "Fin de tour",
            (39, 174, 96),
            (46, 204, 113),
        )
        recruit_y = 548
        bw = UI_WIDTH - 50
        bh = 28
        sp = 4
        x = self.panel_x + 25

        def make_btn(index, text, color, hover):
            return Button(x, recruit_y + (bh + sp) * index, bw, bh, text, color, hover)

        self.btn_recruit_swordsman = make_btn(0, "Spadassin", (41, 128, 185), (52, 152, 219))
        self.btn_recruit_crossbowman = make_btn(1, "Arbalétrier", (142, 68, 173), (155, 89, 182))
        self.btn_recruit_cavalry = make_btn(2, "Cavalerie", (230, 126, 34), (243, 156, 18))
        self.btn_build_city = make_btn(3, f"Construire ville ({CITY_COST} or)", (39, 174, 96), (46, 204, 113))
        self.btn_build_bridge = make_btn(4, "Construire pont", (127, 101, 65), (148, 122, 86))
        self.btn_embark = make_btn(5, "Embarquer", (40, 90, 140), (55, 120, 175))
        self.btn_disembark = make_btn(5, "Débarquer", (40, 110, 90), (55, 140, 110))
        self.btn_move_army = make_btn(6, "Déplacer armée", (52, 73, 94), (71, 94, 121))
        self.btn_ranged_attack = make_btn(7, "Tir à distance", (120, 70, 170), (140, 90, 190))
        self.btn_fortify = make_btn(8, "Fortifier", (80, 110, 90), (96, 130, 108))
        self.btn_research = Button(self.panel_x + 25, WINDOW_HEIGHT - 150, bw, 34, "Rechercher tech", (90, 110, 150), (105, 130, 170))
        self.current_tab = "actions"
        tab_width = (UI_WIDTH - 60) // 3
        self.btn_tab_actions = Button(self.panel_x + 20, 488, tab_width, 28, "Actions", (70, 80, 95), (90, 100, 115))
        self.btn_tab_events = Button(self.panel_x + 25 + tab_width, 488, tab_width, 28, "Journal", (70, 80, 95), (90, 100, 115))
        self.btn_tab_stats = Button(self.panel_x + 30 + tab_width * 2, 488, tab_width, 28, "Stats", (70, 80, 95), (90, 100, 115))

    def draw(self, game):
        pygame.draw.rect(self.screen, UI_BG_COLOR, (self.panel_x, self.panel_y, self.panel_width, self.panel_height))
        pygame.draw.line(self.screen, (80, 80, 85), (self.panel_x, 0), (self.panel_x, WINDOW_HEIGHT), 2)

        pygame.draw.rect(self.screen, (22, 24, 30), (0, 0, GRID_COLS * CELL_SIZE, 36))
        ui_country = game.get_ui_country()
        active = game.current_player_country
        turn_label = f"{COUNTRY_NAMES[active]} (IA)" if game.game_mode == "solo" and active != ui_country else COUNTRY_NAMES[active]
        suffix = ""
        if getattr(game, "fx", None) and game.fx.is_busy():
            suffix = " | ..."
        elif game.ai_turn_pending:
            suffix = " | IA..."
        elif game.pause_menu.open:
            suffix = " | Pause"
        top = self.font_small.render(
            f"Tour {game.turn_number}  ·  {turn_label}  ·  Or {game.players[ui_country].gold}  ·  "
            f"+{game.last_income} / -{game.last_upkeep}{suffix}",
            True,
            (220, 220, 220),
        )
        self.screen.blit(top, (10, 10))

        y = 16
        self.screen.blit(self.font_title.render("The World Is Ours", True, UI_TITLE_COLOR), (self.panel_x + 20, y))
        y += 36
        player = game.players[ui_country]
        self.draw_section_title("Royaume", y)
        y += 28
        pygame.draw.circle(self.screen, COUNTRY_COLORS[ui_country], (self.panel_x + 30, y + 10), 8)
        self.screen.blit(self.font_normal.render(COUNTRY_NAMES[ui_country], True, UI_TEXT_COLOR), (self.panel_x + 50, y))
        y += 28
        trait = player.trait_info()
        if trait:
            self.screen.blit(self.font_small.render(trait["name"], True, (200, 190, 140)), (self.panel_x + 30, y))
            y += 22
        self.screen.blit(self.font_normal.render(f"Or : {player.gold}", True, (255, 215, 0)), (self.panel_x + 30, y))
        y += 32

        if game.selected_cell:
            self.draw_section_title("Case sélectionnée", y)
            y += 28
            cell = game.selected_cell
            lines = [
                f"({cell.x}, {cell.y})  {TERRAIN_FULL_NAMES[cell.terrain]}",
                COUNTRY_NAMES[cell.country] if cell.country != Country.NONE else "Neutre",
            ]
            if cell.is_capital:
                lines.append("Capitale")
            elif cell.is_city:
                lines.append("Ville")
            for line in lines:
                self.screen.blit(self.font_small.render(line, True, UI_TEXT_COLOR), (self.panel_x + 30, y))
                y += 20
            if cell.army:
                army = cell.army
                ship = " (navire)" if army.embarked else ""
                self.screen.blit(
                    self.font_small.render(
                        f"{UNIT_NAMES[army.unit_type]}{ship}  x{army.count}/{MAX_UNITS_PER_ARMY}",
                        True,
                        (255, 255, 140),
                    ),
                    (self.panel_x + 30, y),
                )
                y += 20
                move_range = army.movement_range(game.players.get(army.country))
                self.screen.blit(
                    self.font_small.render(f"Portée {move_range}  ·  PM {army.movement_left}", True, UI_TEXT_COLOR),
                    (self.panel_x + 30, y),
                )
                y += 22

        self.btn_tab_actions.draw(self.screen, self.font_small)
        self.btn_tab_events.draw(self.screen, self.font_small)
        self.btn_tab_stats.draw(self.screen, self.font_small)
        tab_label = {"actions": "Actions", "events": "Journal", "stats": "Stats"}[self.current_tab]
        self.draw_section_title(tab_label, 524)
        recruit_y = 558

        if self.current_tab == "actions" and game.selected_cell:
            human_turn = game.is_human_turn()
            already_recruited = game.selected_cell.last_recruit_turn == game.turn_number
            can_recruit = (
                human_turn
                and game.selected_cell.country == ui_country
                and (game.selected_cell.is_city or game.selected_cell.is_capital)
                and game.selected_cell.terrain not in (TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE)
                and not already_recruited
            )
            can_build_city = (
                human_turn
                and game.selected_cell.country == ui_country
                and not game.selected_cell.is_city
                and not game.selected_cell.is_capital
                and game.selected_cell.terrain not in (TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE)
                and not game.selected_cell.army
            )
            can_build_bridge = human_turn and game.selected_cell.country == ui_country and game.selected_cell.terrain != TerrainType.WATER
            can_move = human_turn and game.selected_cell.army and game.selected_cell.army.country == ui_country
            if can_recruit:
                self.btn_recruit_swordsman.text = f"Spadassin ({player.unit_cost(UnitType.SWORDSMAN)} or)"
                self.btn_recruit_crossbowman.text = f"Arbalétrier ({player.unit_cost(UnitType.CROSSBOWMAN)} or)"
                self.btn_recruit_cavalry.text = f"Cavalerie ({player.unit_cost(UnitType.CAVALRY)} or)"
                self.btn_recruit_swordsman.draw(self.screen, self.font_small)
                self.btn_recruit_crossbowman.draw(self.screen, self.font_small)
                self.btn_recruit_cavalry.draw(self.screen, self.font_small)
            elif already_recruited and (game.selected_cell.is_city or game.selected_cell.is_capital):
                self.screen.blit(
                    self.font_small.render("Cette ville a déjà recruté", True, (180, 140, 140)),
                    (self.panel_x + 28, recruit_y + 8),
                )
            if can_build_city:
                self.btn_build_city.draw(self.screen, self.font_small)
            if can_build_bridge:
                self.btn_build_bridge.text = f"Construire pont ({player.bridge_cost()} or)"
                self.btn_build_bridge.draw(self.screen, self.font_small)
            if can_move and not game.selected_cell.army.embarked:
                self.btn_embark.text = f"Embarquer ({player.embark_cost()} or)"
                self.btn_embark.draw(self.screen, self.font_small)
            if can_move and game.selected_cell.army.embarked:
                label = "Débarquer ici" if game.selected_cell.terrain == TerrainType.BEACH else "Débarquer"
                self.btn_disembark.text = label
                self.btn_disembark.draw(self.screen, self.font_small)
            if can_move:
                self.btn_move_army.draw(self.screen, self.font_small)
                if not game.selected_cell.army.embarked:
                    self.btn_fortify.draw(self.screen, self.font_small)
                if game.selected_cell.army.unit_type == UnitType.CROSSBOWMAN:
                    self.btn_ranged_attack.draw(self.screen, self.font_small)
        elif self.current_tab == "actions":
            self.screen.blit(self.font_small.render("Clique une armée pour la déplacer.", True, (150, 150, 150)), (self.panel_x + 28, recruit_y + 24))
            self.screen.blit(self.font_small.render("Espace : fin de tour.", True, (150, 150, 150)), (self.panel_x + 28, recruit_y + 46))
        elif self.current_tab == "events":
            y = recruit_y
            for msg in game.event_log[-10:]:
                self.screen.blit(self.font_small.render(msg[:44], True, (190, 190, 190)), (self.panel_x + 24, y))
                y += 20
        else:
            y = recruit_y
            for country, count in self.count_territories(game).items():
                if country == Country.NONE or count <= 0:
                    continue
                pygame.draw.circle(self.screen, COUNTRY_COLORS[country], (self.panel_x + 30, y + 8), 6)
                self.screen.blit(self.font_small.render(f"{COUNTRY_NAMES[country]} : {count} cases", True, UI_TEXT_COLOR), (self.panel_x + 45, y))
                y += 20
            y += 8
            if trait:
                self.screen.blit(self.font_small.render("Identité :", True, (190, 210, 230)), (self.panel_x + 24, y))
                y += 20
                self.screen.blit(self.font_small.render(trait["name"], True, (220, 200, 140)), (self.panel_x + 30, y))
                y += 18
                self.screen.blit(self.font_small.render(trait["blurb"], True, (170, 170, 175)), (self.panel_x + 30, y))
                y += 24
            self.screen.blit(self.font_small.render("Techs :", True, (190, 210, 230)), (self.panel_x + 24, y))
            y += 20
            if player.unlocked_techs:
                for tech in TECH_TREE:
                    if tech["id"] in player.unlocked_techs:
                        self.screen.blit(self.font_small.render(f"- {tech['name']}", True, (170, 220, 170)), (self.panel_x + 30, y))
                        y += 18
            else:
                self.screen.blit(self.font_small.render("- Aucune", True, (150, 150, 150)), (self.panel_x + 30, y))

        self.btn_research.draw(self.screen, self.font_small)
        next_tech = player.get_next_tech()
        if next_tech:
            line = f"Tech : {next_tech['name']} ({next_tech['cost']} or)"
        else:
            line = "Arbre techno terminé"
        self.screen.blit(self.font_small.render(line, True, (170, 190, 220)), (self.panel_x + 28, WINDOW_HEIGHT - 112))
        self.btn_end_turn.draw(self.screen, self.font_normal)

    def handle_event(self, event, game):
        if self.btn_end_turn.handle_event(event):
            return "end_turn"
        if self.btn_research.handle_event(event):
            return "research_next"
        if self.btn_tab_actions.handle_event(event):
            self.current_tab = "actions"
            return None
        if self.btn_tab_events.handle_event(event):
            self.current_tab = "events"
            return None
        if self.btn_tab_stats.handle_event(event):
            self.current_tab = "stats"
            return None

        selected_cell = game.selected_cell
        current_country = game.get_ui_country()
        already_recruited = selected_cell and selected_cell.last_recruit_turn == game.turn_number
        can_recruit = (
            selected_cell
            and selected_cell.country == current_country
            and game.is_human_turn()
            and (selected_cell.is_city or selected_cell.is_capital)
            and selected_cell.terrain not in (TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE)
            and not already_recruited
        )
        can_build_city = (
            selected_cell
            and selected_cell.country == current_country
            and not selected_cell.is_city
            and not selected_cell.is_capital
            and selected_cell.terrain not in (TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE)
            and not selected_cell.army
        )
        can_build_bridge = selected_cell and selected_cell.country == current_country and selected_cell.terrain != TerrainType.WATER
        can_move = selected_cell and selected_cell.army and selected_cell.army.country == current_country

        if can_build_city and self.btn_build_city.handle_event(event):
            return "build_city"
        if can_build_bridge and self.btn_build_bridge.handle_event(event):
            return "build_bridge"
        if can_move and selected_cell.army.embarked and self.btn_disembark.handle_event(event):
            return "disembark_mode"
        if can_move and not selected_cell.army.embarked and self.btn_embark.handle_event(event):
            return "embark_mode"
        if can_move and self.btn_move_army.handle_event(event):
            return "move_army"
        if can_move and not selected_cell.army.embarked and self.btn_fortify.handle_event(event):
            return "fortify"
        if can_move and selected_cell.army.unit_type == UnitType.CROSSBOWMAN and self.btn_ranged_attack.handle_event(event):
            return "ranged_attack_mode"
        if can_recruit and self.btn_recruit_swordsman.handle_event(event):
            return ("recruit", UnitType.SWORDSMAN)
        if can_recruit and self.btn_recruit_crossbowman.handle_event(event):
            return ("recruit", UnitType.CROSSBOWMAN)
        if can_recruit and self.btn_recruit_cavalry.handle_event(event):
            return ("recruit", UnitType.CAVALRY)
        return None

    def draw_section_title(self, title, y):
        self.screen.blit(self.font_normal.render(title, True, UI_TITLE_COLOR), (self.panel_x + 20, y))
        pygame.draw.line(self.screen, (80, 80, 85), (self.panel_x + 20, y + 23), (self.panel_x + UI_WIDTH - 20, y + 23), 1)

    def count_territories(self, game):
        counts = {country: 0 for country in Country}
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                if game.grid[x][y].country != Country.NONE:
                    counts[game.grid[x][y].country] += 1
        return counts
