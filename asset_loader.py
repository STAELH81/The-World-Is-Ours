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
        self.ship = None
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
        image = pygame.image.load(path)
        try:
            image = image.convert_alpha()
        except pygame.error:
            image = image.convert()
        return pygame.transform.smoothscale(image, size)

    def _knockout_black_background(self, surf, limit=22):
        """Turn the black studio backdrop transparent, keep the drawing."""
        if surf is None:
            return None
        try:
            work = surf.convert_alpha()
        except pygame.error:
            work = surf.copy()
        width, height = work.get_size()

        def is_backdrop(px, py):
            color = work.get_at((px, py))
            return color[0] <= limit and color[1] <= limit and color[2] <= limit

        seen = set()
        queue = []
        for start in ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)):
            if is_backdrop(*start):
                queue.append(start)
        while queue:
            x, y = queue.pop()
            if (x, y) in seen or not (0 <= x < width and 0 <= y < height):
                continue
            if not is_backdrop(x, y):
                continue
            seen.add((x, y))
            work.set_at((x, y), (0, 0, 0, 0))
            queue.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
        return work

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
                [
                    "units/unit_swordsman.png",
                    "units/swordsman.png",
                    "units/spadassin.png",
                    "swordsman.png",
                    "spadassin.png",
                ],
                ("swordsman", "spadassin", "epee", "sword"),
                unit,
            ),
            UnitType.CROSSBOWMAN: self._pick(
                [
                    "units/unit_crossbowman.png",
                    "units/crossbowman.png",
                    "units/arbaletrier.png",
                    "units/arbalete.png",
                    "crossbowman.png",
                ],
                ("crossbow", "arbalet", "archer"),
                unit,
            ),
            UnitType.SPEARMAN: self._pick(
                [
                    "units/unit_spearman.png",
                    "units/unit_lancier.png",
                    "units/spearman.png",
                    "units/lancier.png",
                    "spearman.png",
                    "lancier.png",
                ],
                ("spearman", "lancier", "lancer", "pique", "pike"),
                unit,
            ),
            UnitType.CAVALRY: self._pick(
                [
                    "units/unit_cavalry.png",
                    "units/cavalry.png",
                    "units/cavalerie.png",
                    "cavalry.png",
                    "cavalerie.png",
                ],
                ("cavalry", "cavalerie", "horse", "cheval"),
                unit,
            ),
            UnitType.CATAPULT: self._pick(
                [
                    "units/unit_catapult.png",
                    "units/unit_catapulte.png",
                    "units/catapult.png",
                    "units/catapulte.png",
                    "catapult.png",
                    "catapulte.png",
                ],
                ("catapult", "catapulte", "cata", "siege", "trebuchet"),
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
        self.ship = self._pick(
            [
                "units/unit_ship.png",
                "units/unit_bateau.png",
                "units/ship.png",
                "units/bateau.png",
                "ship.png",
                "bateau.png",
            ],
            ("ship", "bateau", "navire", "boat", "galere"),
            unit,
        )
        for key, sprite in list(self.units.items()):
            self.units[key] = self._knockout_black_background(sprite)
        self.ship = self._knockout_black_background(self.ship)
        for key, sprite in list(self.buildings.items()):
            self.buildings[key] = self._knockout_black_background(sprite)

    def summarize(self):
        lines = ["Sprites :"]
        for unit_type, label in (
            (UnitType.SWORDSMAN, "Spadassin"),
            (UnitType.SPEARMAN, "Lancier"),
            (UnitType.CROSSBOWMAN, "Arbalétrier"),
            (UnitType.CAVALRY, "Cavalerie"),
            (UnitType.CATAPULT, "Catapulte"),
        ):
            found = "PNG" if self.units.get(unit_type) else "dessin par défaut"
            lines.append(f"  {label}: {found}")
        lines.append(f"  Bateau: {'PNG' if self.ship else 'dessin par défaut'}")
        for key, label in (("capital", "Capitale"), ("city", "Ville")):
            found = "PNG" if self.buildings.get(key) else "dessin par défaut"
            lines.append(f"  {label}: {found}")
        text = "\n".join(lines)
        print(text)
        if self._index:
            print("PNG trouvés :")
            for path in sorted(self._index.values()):
                print(f"  {path}")
        else:
            print("PNG trouvés : (aucun dans assets/)")
        return text
