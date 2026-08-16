"""Génération procédurale de carte (îles, territoires, capitales)."""

import random
from constants import *

PLAYABLE_COUNTRIES = [
    Country.RED,
    Country.GREEN,
    Country.BLUE,
    Country.YELLOW,
    Country.ORANGE,
]

ISLAND_BASE_SIZE = 50
ISLAND_SIZE_VARIANCE = 3
MIN_CENTER_DISTANCE = 7
MIN_ISLAND_SIZE = 40
MAX_ISLAND_SIZE = 56


class MapGenerator:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)

    def generate(self, game):
        """Remplit la grille du jeu avec une nouvelle carte."""
        self._clear_grid(game)
        centers = []
        islands = []
        claimed = set()

        slots = [
            (6, 5),
            (16, 4),
            (25, 5),
            (10, 13),
            (22, 13),
        ]
        for country, (sx, sy) in zip(PLAYABLE_COUNTRIES, slots):
            center = (
                max(3, min(GRID_COLS - 4, sx + self.rng.randint(-1, 1))),
                max(3, min(GRID_ROWS - 4, sy + self.rng.randint(-1, 1))),
            )
            centers.append(center)
            target_size = ISLAND_BASE_SIZE + self.rng.randint(
                -ISLAND_SIZE_VARIANCE, ISLAND_SIZE_VARIANCE
            )
            land = self._grow_island(game, center, target_size, forbidden=claimed)
            claimed |= land
            islands.append(land)
            game.apply_country(list(land), country)

        self._balance_island_sizes(game, islands)

        for land in islands:
            self._scatter_terrain(game, land)

        capitals = {}
        for country, land in zip(PLAYABLE_COUNTRIES, islands):
            capitals[country] = self._pick_capital_tile(land)

        game.add_beaches()
        game.place_capitals_from_dict(capitals)
        game.map_seed = self.rng.randint(0, 2**31 - 1)

    def _clear_grid(self, game):
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = game.grid[x][y]
                cell.terrain = TerrainType.WATER
                cell.country = Country.NONE
                cell.is_capital = False
                cell.is_city = False
                cell.army = None
                cell.bridge_hp = 0
                cell.capital_owner = Country.NONE
                cell.city_owner = Country.NONE
                cell.last_recruit_turn = -1
                cell.garrison_ready = True
                cell.discovered_by = set()

    def _pick_island_center(self, existing):
        for _ in range(300):
            x = self.rng.randint(3, GRID_COLS - 4)
            y = self.rng.randint(3, GRID_ROWS - 4)
            if all(abs(x - cx) + abs(y - cy) >= MIN_CENTER_DISTANCE for cx, cy in existing):
                return (x, y)
        return (
            self.rng.randint(3, GRID_COLS - 4),
            self.rng.randint(3, GRID_ROWS - 4),
        )

    def _grow_island(self, game, center, target_size, forbidden=None):
        cx, cy = center
        blocked = set(forbidden or ())
        land = {(cx, cy)}
        if (cx, cy) in blocked:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (0, 2)):
                nx, ny = cx + dx, cy + dy
                if 1 <= nx < GRID_COLS - 1 and 1 <= ny < GRID_ROWS - 1 and (nx, ny) not in blocked:
                    land = {(nx, ny)}
                    break
        frontier = list(land)
        blocked |= land

        while len(land) < target_size and frontier:
            fx, fy = self.rng.choice(frontier)
            neighbors = []
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = fx + dx, fy + dy
                if not (1 <= nx < GRID_COLS - 1 and 1 <= ny < GRID_ROWS - 1):
                    continue
                if (nx, ny) in land or (nx, ny) in blocked:
                    continue
                neighbors.append((nx, ny))

            if not neighbors:
                frontier.remove((fx, fy))
                continue

            pick = self.rng.choice(neighbors)
            land.add(pick)
            blocked.add(pick)
            frontier.append(pick)
            game.grid[pick[0]][pick[1]].terrain = TerrainType.PLAIN

        for x, y in land:
            game.grid[x][y].terrain = TerrainType.PLAIN
        return land

    def _balance_island_sizes(self, game, islands):
        """Rééquilibre légèrement les îles trop petites ou trop grandes."""
        sizes = [len(land) for land in islands]
        if not sizes:
            return

        while True:
            sizes = [len(land) for land in islands]
            largest_idx = sizes.index(max(sizes))
            smallest_idx = sizes.index(min(sizes))
            if sizes[largest_idx] - sizes[smallest_idx] <= 6:
                break

            donor = islands[largest_idx]
            receiver_land = islands[smallest_idx]
            if len(donor) <= MIN_ISLAND_SIZE:
                break

            border_tile = None
            for x, y in donor:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in donor:
                        border_tile = (x, y)
                        break
                if border_tile:
                    break
            if not border_tile:
                break

            donor.remove(border_tile)
            receiver_land.add(border_tile)
            x, y = border_tile
            game.grid[x][y].terrain = TerrainType.PLAIN
            game.grid[x][y].country = PLAYABLE_COUNTRIES[smallest_idx]

    def _scatter_terrain(self, game, land):
        land_list = list(land)
        self.rng.shuffle(land_list)
        mountain_count = max(3, len(land_list) // 10)
        forest_count = max(4, len(land_list) // 7)

        for x, y in land_list[:mountain_count]:
            game.grid[x][y].terrain = TerrainType.MOUNTAIN
        for x, y in land_list[mountain_count : mountain_count + forest_count]:
            if game.grid[x][y].terrain == TerrainType.PLAIN:
                game.grid[x][y].terrain = TerrainType.FOREST

    def _pick_capital_tile(self, land):
        """Case la plus « intérieure » de l'île (max distance à l'eau)."""
        best = None
        best_score = -1
        for x, y in land:
            score = 0
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if (nx, ny) not in land:
                    score += 1
            interior = -score
            if interior > best_score:
                best_score = interior
                best = (x, y)
        return best or next(iter(land))
