import os
import pygame
from constants import TerrainType, Country, UnitType, CELL_SIZE


class AssetLoader:
    """Loads and caches game sprites with pre-scaled sizes."""

    def __init__(self, base_path="assets"):
        self.base_path = base_path
        self.terrain = {}
        self.overlays = {}
        self.units = {}
        self.buildings = {}
        self._load_all()

    def _safe_load(self, relative_path, size):
        full_path = os.path.join(self.base_path, relative_path)
        if not os.path.exists(full_path):
            return None

        image = pygame.image.load(full_path).convert_alpha()
        return pygame.transform.smoothscale(image, size)

    def _load_all(self):
        # Terrain tiles rendered at one full cell.
        self.terrain = {
            TerrainType.PLAIN: self._safe_load("terrain/terrain_plain.png", (CELL_SIZE, CELL_SIZE)),
            TerrainType.FOREST: self._safe_load("terrain/terrain_forest.png", (CELL_SIZE, CELL_SIZE)),
            TerrainType.MOUNTAIN: self._safe_load("terrain/terrain_mountain.png", (CELL_SIZE, CELL_SIZE)),
            TerrainType.WATER: self._safe_load("terrain/terrain_water.png", (CELL_SIZE, CELL_SIZE)),
            TerrainType.BEACH: self._safe_load("terrain/terrain_beach.png", (CELL_SIZE, CELL_SIZE)),
            TerrainType.BRIDGE: self._safe_load("terrain/terrain_bridge.png", (CELL_SIZE, CELL_SIZE)),
        }

        # Country border overlays (drawn over terrain).
        self.overlays = {
            Country.RED: self._safe_load("overlay/border_red.png", (CELL_SIZE, CELL_SIZE)),
            Country.BLUE: self._safe_load("overlay/border_blue.png", (CELL_SIZE, CELL_SIZE)),
            Country.GREEN: self._safe_load("overlay/border_green.png", (CELL_SIZE, CELL_SIZE)),
            Country.YELLOW: self._safe_load("overlay/border_yellow.png", (CELL_SIZE, CELL_SIZE)),
            Country.ORANGE: self._safe_load("overlay/border_orange.png", (CELL_SIZE, CELL_SIZE)),
        }

        # Units are smaller than a full tile.
        self.units = {
            UnitType.SWORDSMAN: self._safe_load("units/unit_swordsman.png", (24, 24)),
            UnitType.CROSSBOWMAN: self._safe_load("units/unit_crossbowman.png", (24, 24)),
            UnitType.CAVALRY: self._safe_load("units/unit_cavalry.png", (24, 24)),
        }

        # Buildings.
        self.buildings = {
            "capital": self._safe_load("buildings/capital.png", (22, 22)),
            "city": self._safe_load("buildings/city.png", (18, 18)),
        }
