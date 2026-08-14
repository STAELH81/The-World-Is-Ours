import random
from constants import *
from army import Army


class AI:
    def __init__(self, game):
        self.game = game

    def is_target_allowed(self, attacker_country, target_country):
        if target_country == Country.NONE:
            return False
        truce_turns = self.game.difficulty_cfg.get("ai_truce_turns", 3)
        if (
            self.game.game_mode == "solo"
            and attacker_country != Country.RED
            and target_country == Country.RED
            and self.game.turn_number <= truce_turns
        ):
            return False
        return True

    def play_turn(self, country):
        print(f"\n[AI] {COUNTRY_NAMES[country]} reflechit...")
        player = self.game.players[country]

        self._try_research(country, player)
        self._try_build_city(country, player)
        self._try_build_bridge(country, player)
        self._recruit_units(country, player)
        self._move_armies(country)

        print(f"[AI] {COUNTRY_NAMES[country]} termine son tour")

    def _try_research(self, country, player):
        tech = player.get_next_tech()
        if tech and player.gold >= tech["cost"] + 80:
            result = player.research_next()
            if result:
                self.game.log_event(f"[TECH] {COUNTRY_NAMES[country]} debloque {result['name']}")

    def _try_build_city(self, country, player):
        if player.gold < CITY_COST + 60:
            return
        if player.count_cities(self.game.grid) >= player.max_cities_allowed(self.game.grid):
            return

        candidates = []
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                if not self._is_valid_city_site(cell, country):
                    continue
                score = 0
                if cell.is_capital:
                    score += 5
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS:
                        n = self.game.grid[nx][ny]
                        if n.country != country and n.country != Country.NONE:
                            score += 2
                candidates.append((score, cell))

        if not candidates:
            return
        candidates.sort(key=lambda item: item[0], reverse=True)
        cell = candidates[0][1]
        player.spend_gold(CITY_COST)
        cell.is_city = True
        cell.city_owner = country
        self.game.audio.play("build")

    def _recruit_units(self, country, player):
        urban_cells = []
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                if (
                    (cell.is_capital or cell.is_city)
                    and cell.country == country
                    and cell.terrain not in (TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE)
                ):
                    urban_cells.append(cell)

        def urban_priority(cell):
            score = 10 if cell.is_capital else 0
            if cell.army and cell.army.count < MAX_UNITS_PER_ARMY:
                score += 5
            return score

        urban_cells.sort(key=urban_priority, reverse=True)
        recruited = 0
        min_unit_cost = min(UNIT_COSTS.values())

        recruit_limit = self.game.difficulty_cfg.get("ai_recruit_limit", 2)
        for capital_cell in urban_cells:
            if recruited >= recruit_limit or player.gold < min_unit_cost + 40:
                break
            if capital_cell.last_recruit_turn == self.game.turn_number:
                continue

            unit_type = self._pick_recruit_type(player, capital_cell, country)
            if unit_type is None:
                continue

            cost = player.unit_cost(unit_type)
            if player.gold < cost:
                continue
            player.spend_gold(cost)

            if capital_cell.army:
                capital_cell.army.count += 1
            else:
                capital_cell.army = Army(country, unit_type, 1)
                capital_cell.army.refresh_movement(player)
            capital_cell.last_recruit_turn = self.game.turn_number
            recruited += 1

    def _pick_recruit_type(self, player, cell, country):
        if cell.army:
            if cell.army.count >= MAX_UNITS_PER_ARMY:
                return None
            return cell.army.unit_type

        if player.gold >= player.unit_cost(UnitType.CAVALRY):
            return UnitType.CAVALRY
        if player.gold >= player.unit_cost(UnitType.CROSSBOWMAN):
            return UnitType.CROSSBOWMAN
        if player.gold >= player.unit_cost(UnitType.SWORDSMAN):
            return UnitType.SWORDSMAN
        return None

    def _move_armies(self, country):
        armies = []
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                if cell.army and cell.army.country == country:
                    armies.append(cell)
        armies.sort(key=lambda c: self._army_priority(c, country), reverse=True)
        for army_cell in armies:
            if not army_cell.army:
                continue
            step_guard = 0
            while army_cell.army and army_cell.army.movement_left > 0 and step_guard < 4:
                step_guard += 1
                army = army_cell.army
                if army.unit_type == UnitType.CROSSBOWMAN:
                    target = self._best_ranged_target(army_cell, country)
                    if target:
                        self.game.ranged_attack(army_cell, target)
                        continue
                if army.embarked:
                    landing = self._best_disembark_target(army_cell, country)
                    if landing:
                        self.game.disembark_army(army_cell, landing)
                        army_cell = self._follow(army_cell, landing, country)
                        continue
                    sail = self._best_sail_target(army_cell, country)
                    if sail:
                        self.game.move_army(army_cell, sail)
                        army_cell = self._follow(army_cell, sail, country)
                        continue
                    break
                recapture = self._best_recapture_target(army_cell, country)
                if recapture:
                    self.game.move_army(army_cell, recapture)
                    army_cell = self._follow(army_cell, recapture, country)
                    continue
                enemy = self._best_attack_target(army_cell, country)
                if enemy:
                    self.game.move_army(army_cell, enemy)
                    army_cell = self._follow(army_cell, enemy, country)
                    continue
                if not self._can_reach_objective_by_land(army_cell, country):
                    embark_cell = self._best_embark_tile(army_cell)
                    player = self.game.players[country]
                    if embark_cell and player.gold >= player.embark_cost():
                        self.game.embark_army(army_cell, embark_cell)
                        army_cell = self._follow(army_cell, embark_cell, country)
                        continue
                move_to = self._best_move_toward_objective(army_cell, country)
                if move_to:
                    self.game.move_army(army_cell, move_to)
                    army_cell = self._follow(army_cell, move_to, country)
                else:
                    break

    def _follow(self, old_cell, dest, country):
        if dest.army and dest.army.country == country:
            return dest
        if old_cell.army and old_cell.army.country == country:
            return old_cell
        return dest

    def _can_reach_objective_by_land(self, from_cell, country):
        objective = self._nearest_enemy_capital(from_cell, country)
        if not objective or not from_cell.army:
            return True
        was_embarked = from_cell.army.embarked
        from_cell.army.embarked = False
        path = self.game.find_path(from_cell, objective, GRID_COLS + GRID_ROWS, from_cell.army)
        from_cell.army.embarked = was_embarked
        return bool(path)

    def _best_embark_tile(self, from_cell):
        targets = self.game.get_embark_targets(from_cell)
        if not targets:
            return None
        objective = self._nearest_enemy_capital(from_cell, from_cell.army.country)
        best = None
        best_score = 999
        for x, y in targets:
            cell = self.game.grid[x][y]
            dist = abs(x - from_cell.x) + abs(y - from_cell.y)
            if objective:
                dist += abs(x - objective.x) + abs(y - objective.y)
            if dist < best_score:
                best_score = dist
                best = cell
        return best

    def _best_disembark_target(self, from_cell, country):
        targets = self.game.get_disembark_targets(from_cell)
        if not targets:
            return None
        # Prefer stepping off the current beach in place.
        if (from_cell.x, from_cell.y) in targets:
            return from_cell
        objective = self._nearest_enemy_capital(from_cell, country)
        best = None
        best_score = -9999
        for x, y in targets:
            cell = self.game.grid[x][y]
            score = 50
            if cell.army and cell.army.country != country:
                score += 40
            if cell.is_capital:
                score += 80
            if cell.is_city:
                score += 30
            if objective:
                score -= abs(x - objective.x) + abs(y - objective.y)
            if score > best_score:
                best_score = score
                best = cell
        return best

    def _best_sail_target(self, from_cell, country):
        objective = self._nearest_enemy_capital(from_cell, country)
        if not objective or not from_cell.army:
            return None
        movement_range = from_cell.army.movement_left
        best = None
        best_dist = abs(from_cell.x - objective.x) + abs(from_cell.y - objective.y)
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                target = self.game.grid[x][y]
                path = self.game.find_path(from_cell, target, movement_range, from_cell.army)
                if not path:
                    continue
                dist = abs(x - objective.x) + abs(y - objective.y)
                shore = 8 if any(n.terrain in LAND_TERRAINS or n.terrain == TerrainType.BEACH for n in self.game._neighbors(target)) else 0
                score_dist = dist - shore
                if score_dist < best_dist:
                    best_dist = score_dist
                    best = target
        return best

    def _try_build_bridge(self, country, player):
        if player.gold < player.bridge_cost() + 50:
            return
        self.game.compute_bridge_targets()
        if not self.game.bridge_targets:
            return
        objective = None
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                if cell.is_capital and cell.country not in (country, Country.NONE) and self.is_target_allowed(country, cell.country):
                    objective = cell
                    break
            if objective:
                break
        best = None
        best_dist = 999
        for x, y in self.game.bridge_targets:
            dist = 0 if not objective else abs(x - objective.x) + abs(y - objective.y)
            if dist < best_dist:
                best_dist = dist
                best = self.game.grid[x][y]
        if best:
            self.game.build_bridge_on_cell(best)

    def _army_priority(self, army_cell, country):
        score = 0
        cap = self._nearest_enemy_capital(army_cell, country)
        if cap:
            dist = abs(army_cell.x - cap.x) + abs(army_cell.y - cap.y)
            score += max(0, 40 - dist)
        if army_cell.army.unit_type == UnitType.CAVALRY:
            score += 3
        return score

    def _nearest_enemy_capital(self, from_cell, country):
        best = None
        best_dist = 999
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                if not cell.is_capital:
                    continue
                if cell.country == country or cell.country == Country.NONE:
                    continue
                if not self.is_target_allowed(country, cell.country):
                    continue
                dist = abs(from_cell.x - x) + abs(from_cell.y - y)
                if dist < best_dist:
                    best_dist = dist
                    best = cell
        return best

    def _target_score(self, from_cell, target, country, distance):
        score = 100 - distance * 8
        if target.is_capital and target.country != country:
            score += 80
        if target.is_city and target.country != country:
            score += 35
        if target.army and target.army.country != country:
            score += 45
        if not self.is_target_allowed(country, target.country):
            score -= 200
        return score

    def _best_recapture_target(self, from_cell, country):
        """Priorite: reprendre capitale/villes du royaume occupees par l'ennemi."""
        best = None
        best_distance = 999
        movement_range = from_cell.army.movement_left

        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                own_urban = (
                    (cell.is_capital and cell.capital_owner == country)
                    or (cell.is_city and cell.city_owner == country)
                )
                if not own_urban or cell.country == country:
                    continue
                path = self.game.find_path(from_cell, cell, movement_range, from_cell.army)
                if not path:
                    continue
                distance = len(path)
                if distance < best_distance:
                    best_distance = distance
                    best = cell
        return best

    def _best_attack_target(self, from_cell, country):
        best = None
        best_score = -9999
        movement_range = from_cell.army.movement_left

        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = self.game.grid[x][y]
                if cell.country == country or cell.country == Country.NONE:
                    continue
                path = self.game.find_path(from_cell, cell, movement_range, from_cell.army)
                if not path:
                    continue
                score = self._target_score(from_cell, cell, country, len(path))
                if score > best_score:
                    best_score = score
                    best = cell
        return best

    def _best_ranged_target(self, from_cell, country):
        targets = self.game.get_ranged_targets(from_cell)
        if not targets:
            return None
        best = None
        best_score = -9999
        for tx, ty in targets:
            cell = self.game.grid[tx][ty]
            dist = abs(from_cell.x - tx) + abs(from_cell.y - ty)
            score = self._target_score(from_cell, cell, country, dist)
            if score > best_score:
                best_score = score
                best = cell
        return best

    def _best_move_toward_objective(self, from_cell, country):
        objective = self._nearest_enemy_capital(from_cell, country)
        if not objective:
            return None

        movement_range = from_cell.army.movement_left
        best_move = None
        best_dist = abs(from_cell.x - objective.x) + abs(from_cell.y - objective.y)

        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                if abs(from_cell.x - x) + abs(from_cell.y - y) > movement_range:
                    continue
                target_cell = self.game.grid[x][y]
                if target_cell.terrain == TerrainType.WATER:
                    continue
                path = self.game.find_path(from_cell, target_cell, movement_range, from_cell.army)
                if not path:
                    continue
                if target_cell.army and target_cell.army.country == country:
                    if target_cell.army.unit_type != from_cell.army.unit_type:
                        continue
                dist = abs(x - objective.x) + abs(y - objective.y)
                if dist < best_dist:
                    best_dist = dist
                    best_move = target_cell
        return best_move

    def _is_valid_city_site(self, cell, country):
        return (
            cell.country == country
            and not cell.is_capital
            and not cell.is_city
            and not cell.army
            and cell.terrain not in (TerrainType.WATER, TerrainType.BEACH, TerrainType.BRIDGE)
        )
