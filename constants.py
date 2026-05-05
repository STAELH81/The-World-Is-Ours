from enum import Enum

# Taille de la grille
GRID_COLS = 20
GRID_ROWS = 30
CELL_SIZE = 34

# UI
UI_WIDTH = 380
WINDOW_WIDTH = GRID_COLS * CELL_SIZE + UI_WIDTH  # MODIFIÉ
WINDOW_HEIGHT = GRID_ROWS * CELL_SIZE

# Types de terrain
class TerrainType(Enum):
    PLAIN = 0
    MOUNTAIN = 1
    FOREST = 2
    WATER = 3
    BEACH = 4
    BRIDGE = 5

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
    TerrainType.BRIDGE: (127, 101, 65),
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
    TerrainType.BRIDGE: "Pont",
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
    UnitType.SWORDSMAN: 40,
    UnitType.CROSSBOWMAN: 55,
    UnitType.CAVALRY: 70,
}
MAX_UNITS_PER_ARMY = 16

# Coût d'entretien par tour
UNIT_UPKEEP = 5 

# Villes
CITY_COST = 150  # Coût de construction d'une ville
CITY_INCOME = 50  # Or généré par ville par tour
CITY_TERRITORY_REQUIREMENT = 25  # Cases nécessaires pour 1 ville
BRIDGE_COST = 90

# Stats de combat (pour plus tard)
UNIT_STATS = {
    UnitType.SWORDSMAN: {"attack": 3, "defense": 4},
    UnitType.CROSSBOWMAN: {"attack": 3, "defense": 2},
    UnitType.CAVALRY: {"attack": 4, "defense": 3},
}

# Mouvement
MOVEMENT_RANGE = 3  # Nombre de cases max par déplacement
UNIT_MOVEMENT_RANGE = {
    UnitType.SWORDSMAN: 2,
    UnitType.CROSSBOWMAN: 3,
    UnitType.CAVALRY: 4,
}
UNIT_RANGED_RANGE = {
    UnitType.CROSSBOWMAN: 2,
}
RANGED_BASE_DAMAGE = 4
FORTIFY_DEFENSE_BONUS = 1

TECH_TREE = [
    {"id": "economy", "name": "Agriculture", "cost": 250},
    {"id": "engineering", "name": "Ingenierie", "cost": 280},
    {"id": "ballistics", "name": "Balistique", "cost": 320},
    {"id": "logistics", "name": "Logistique", "cost": 360},
]

# Visibilité
FOG_RADIUS = 2

# Bonus de combat selon terrain
TERRAIN_DEFENSE_BONUS = {
    TerrainType.PLAIN: 0,
    TerrainType.MOUNTAIN: 2,  # +2 défense en montagne
    TerrainType.FOREST: 1,    # +1 défense en forêt
    TerrainType.WATER: 0,
    TerrainType.BEACH: 0,
    TerrainType.BRIDGE: 0,
}