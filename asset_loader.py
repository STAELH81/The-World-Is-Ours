import os
import pygame
from constants import TerrainType, Country, UnitType, CELL_SIZE


class AssetLoader:
    """Charge les PNG du dossier assets, avec plusieurs noms de fichiers acceptés."""

    def __init__(self, base_path="assets"):
        self.base_path = base_path
        self.terrain = {}
        self.overlays = {}
        self.units = {}
        self.buildings = {}
        self._index = {}
        self._index_files()
        self._load_all()

    def _index_files(self):
        if not os.path.isdir(self.base_path):
            return
        for root, _dirs, files in os.walk(self.base_path):
            for name in files:
                lower = name.lower()
                if lower.endswith(".png") or lower.endswith(".jpg") or lower.endswith(".webp"):
                    self._index[lower] = os.path.join(root, name)

    def _load_path(self, path, size):
        if not path or not os.path.exists(path):
            return None
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(image, size)

    def _load_named(self, filenames, size):
        for name in filenames:
            path = os.path.join(self.base_path, name.replace("/", os.sep))
            loaded = self._load_path(path, size)
            if loaded:
                return loaded
        for name in filenames:
            keyed = os.path.basename(name).lower()
            if keyed in self._index:
                loaded = self._load_path(self._index[keyed], size)
                if loaded:
                    return loaded
        return None

    def _load_keywords(self, keywords, size):
        for filename, path in self._index.items():
            stem = os.path.splitext(filename)[0]
            if any(word in stem for word in keywords):
                loaded = self._load_path(path, size)
                if loaded:
                    return loaded
        return None

    def _pick(self, filenames, keywords, size):
        return self._load_named(filenames, size) or self._load_keywords(keywords, size)

    def _load_all(self):
        tile = (CELL_SIZE, CELL_SIZE)
        unit = (max(26, CELL_SIZE - 4), max(26, CELL_SIZE - 4))
        building = (max(22, CELL_SIZE - 8), max(22, CELL_SIZE - 8))

        self.terrain = {
            TerrainType.PLAIN: self._pick(
                ["terrain/terrain_plain.png", "terrain/plain.png", "plain.png"],
                ("plain", "plaine", "grass"),
                tile,
            ),
            TerrainType.FOREST: self._pick(
                ["terrain/terrain_forest.png", "terrain/forest.png", "forest.png"],
                ("forest", "foret", "bois"),
                tile,
            ),
            TerrainType.MOUNTAIN: self._pick(
                ["terrain/terrain_mountain.png", "terrain/mountain.png", "mountain.png"],
                ("mountain", "montagne"),
                tile,
            ),
            TerrainType.WATER: self._pick(
                ["terrain/terrain_water.png", "terrain/water.png", "water.png"],
                ("water", "eau", "ocean"),
                tile,
            ),
            TerrainType.BEACH: self._pick(
                ["terrain/terrain_beach.png", "terrain/beach.png", "beach.png"],
                ("beach", "plage", "sand"),
                tile,
            ),
            TerrainType.BRIDGE: self._pick(
                ["terrain/terrain_bridge.png", "terrain/bridge.png", "bridge.png"],
                ("bridge", "pont"),
                tile,
            ),
        }
        self.overlays = {
            Country.RED: self._pick(["overlay/border_red.png"], ("border_red", "rouge"), tile),
            Country.BLUE: self._pick(["overlay/border_blue.png"], ("border_blue", "bleu"), tile),
            Country.GREEN: self._pick(["overlay/border_green.png"], ("border_green", "vert"), tile),
            Country.YELLOW: self._pick(["overlay/border_yellow.png"], ("border_yellow", "jaune"), tile),
            Country.ORANGE: self._pick(["overlay/border_orange.png"], ("border_orange", "orange"), tile),
        }
        self.units = {
            UnitType.SWORDSMAN: self._pick(
                ["units/unit_swordsman.png", "units/swordsman.png", "swordsman.png"],
                ("swordsman", "spadassin", "epee", "sword"),
                unit,
            ),
            UnitType.CROSSBOWMAN: self._pick(
                ["units/unit_crossbowman.png", "units/crossbowman.png", "crossbowman.png"],
                ("crossbow", "arbalet", "archer"),
                unit,
            ),
            UnitType.SPEARMAN: self._pick(
                ["units/unit_spearman.png", "units/spearman.png", "spearman.png"],
                ("spearman", "lancier", "pique", "pike"),
                unit,
            ),
            UnitType.CAVALRY: self._pick(
                ["units/unit_cavalry.png", "units/cavalry.png", "cavalry.png"],
                ("cavalry", "cavalerie", "horse", "cheval"),
                unit,
            ),
            UnitType.CATAPULT: self._pick(
                ["units/unit_catapult.png", "units/catapult.png", "catapult.png"],
                ("catapult", "catapulte", "siege", "trebuchet"),
                unit,
            ),
        }
        self.buildings = {
            "capital": self._pick(
                ["buildings/capital.png", "buildings/palace.png", "capital.png"],
                ("capital", "palais", "castle", "forteresse"),
                building,
            ),
            "city": self._pick(
                ["buildings/city.png", "buildings/ville.png", "city.png"],
                ("city", "ville", "town", "village"),
                (max(18, CELL_SIZE - 12), max(18, CELL_SIZE - 12)),
            ),
        }
