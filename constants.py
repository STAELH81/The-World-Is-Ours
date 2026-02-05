from enum import Enum

# Taille de la grille
GRID_COLS = 20
GRID_ROWS = 30
CELL_SIZE = 32

# UI
UI_WIDTH = 300  # NOUVEAU
WINDOW_WIDTH = GRID_COLS * CELL_SIZE + UI_WIDTH  # MODIFIÉ
WINDOW_HEIGHT = GRID_ROWS * CELL_SIZE

# Types de terrain
class TerrainType(Enum):
    PLAIN = 0
    MOUNTAIN = 1
    FOREST = 2
    WATER = 3
    BEACH = 4

# Pays
class Country(Enum):
    NONE = 0
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    ORANGE = 5

# Couleurs des terrains
TERRAIN_COLORS = {
    TerrainType.PLAIN: (126, 200, 80),
    TerrainType.MOUNTAIN: (107, 66, 38),
    TerrainType.FOREST: (45, 90, 27),
    TerrainType.WATER: (26, 58, 107),
    TerrainType.BEACH: (212, 197, 160),
}

# Couleurs des pays
COUNTRY_COLORS = {
    Country.NONE: (255, 255, 255),
    Country.RED: (192, 57, 43),
    Country.BLUE: (41, 128, 185),
    Country.GREEN: (39, 174, 96),
    Country.YELLOW: (241, 196, 15),
    Country.ORANGE: (230, 126, 34),
}

# Noms complets des pays - NOUVEAU
COUNTRY_NAMES = {
    Country.NONE: "Aucun",
    Country.RED: "Royaume Rouge",
    Country.BLUE: "Royaume Bleu",
    Country.GREEN: "Royaume Vert",
    Country.YELLOW: "Royaume Jaune",
    Country.ORANGE: "Royaume Orange",
}

# Noms des terrains - NOUVEAU (complets)
TERRAIN_FULL_NAMES = {
    TerrainType.PLAIN: "Plaine",
    TerrainType.MOUNTAIN: "Montagne",
    TerrainType.FOREST: "Forêt",
    TerrainType.WATER: "Eau",
    TerrainType.BEACH: "Plage",
}

# Couleurs UI - NOUVEAU
UI_BG_COLOR = (40, 40, 45)
UI_TEXT_COLOR = (220, 220, 220)
UI_TITLE_COLOR = (255, 255, 255)

# Types d'unités
class UnitType(Enum):
    SWORDSMAN = 0  # Spadassin
    CROSSBOWMAN = 1  # Arbalétrier
    CAVALRY = 2  # Cavalerie

# Noms des unités
UNIT_NAMES = {
    UnitType.SWORDSMAN: "Spadassin",
    UnitType.CROSSBOWMAN: "Arbalétrier",
    UnitType.CAVALRY: "Cavalerie",
}

# Icônes/symboles des unités (pour l'affichage)
UNIT_SYMBOLS = {
    UnitType.SWORDSMAN: "⚔",
    UnitType.CROSSBOWMAN: "🏹",
    UnitType.CAVALRY: "🐴",
}

# Coûts de recrutement
UNIT_COSTS = {
    UnitType.SWORDSMAN: 45,
    UnitType.CROSSBOWMAN: 45,
    UnitType.CAVALRY: 45,
}

# Coût d'entretien par tour
UNIT_UPKEEP = 5 

# Villes
CITY_COST = 150  # Coût de construction d'une ville
CITY_INCOME = 50  # Or généré par ville par tour
CITY_TERRITORY_REQUIREMENT = 25  # Cases nécessaires pour 1 ville

# Stats de combat (pour plus tard)
UNIT_STATS = {
    UnitType.SWORDSMAN: {"attack": 3, "defense": 3},
    UnitType.CROSSBOWMAN: {"attack": 4, "defense": 2},
    UnitType.CAVALRY: {"attack": 5, "defense": 2},
}

# Stats de combat (pour plus tard)
UNIT_STATS = {
    UnitType.SWORDSMAN: {"attack": 3, "defense": 3},
    UnitType.CROSSBOWMAN: {"attack": 4, "defense": 2},
    UnitType.CAVALRY: {"attack": 5, "defense": 2},
}