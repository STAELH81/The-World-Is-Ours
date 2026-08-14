from enum import Enum

GRID_COLS = 20
GRID_ROWS = 30
CELL_SIZE = 36

HUD_TOP = 70
MAP_ORIGIN_X = 0
MAP_ORIGIN_Y = HUD_TOP
MAP_PIXEL_WIDTH = GRID_COLS * CELL_SIZE
MAP_PIXEL_HEIGHT = GRID_ROWS * CELL_SIZE
WINDOW_WIDTH = MAP_PIXEL_WIDTH
WINDOW_HEIGHT = HUD_TOP + MAP_PIXEL_HEIGHT


def cell_screen_pos(x, y):
    return MAP_ORIGIN_X + x * CELL_SIZE, MAP_ORIGIN_Y + y * CELL_SIZE


def screen_to_cell(px, py):
    if px < MAP_ORIGIN_X or py < MAP_ORIGIN_Y:
        return None
    cx = (px - MAP_ORIGIN_X) // CELL_SIZE
    cy = (py - MAP_ORIGIN_Y) // CELL_SIZE
    if 0 <= cx < GRID_COLS and 0 <= cy < GRID_ROWS:
        return int(cx), int(cy)
    return None


class TerrainType(Enum):
    PLAIN = 0
    MOUNTAIN = 1
    FOREST = 2
    WATER = 3
    BEACH = 4
    BRIDGE = 5


class Country(Enum):
    NONE = 0
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    ORANGE = 5


LAND_TERRAINS = (TerrainType.PLAIN, TerrainType.MOUNTAIN, TerrainType.FOREST)
SHORE_TERRAINS = LAND_TERRAINS + (TerrainType.BEACH,)
NAVAL_TERRAINS = (TerrainType.WATER, TerrainType.BRIDGE)
DISEMBARK_TERRAINS = SHORE_TERRAINS

TERRAIN_COLORS = {
    TerrainType.PLAIN: (132, 156, 78),
    TerrainType.MOUNTAIN: (128, 108, 78),
    TerrainType.FOREST: (38, 78, 36),
    TerrainType.WATER: (28, 68, 112),
    TerrainType.BEACH: (214, 192, 140),
    TerrainType.BRIDGE: (118, 86, 48),
}

COUNTRY_COLORS = {
    Country.NONE: (255, 255, 255),
    Country.RED: (176, 48, 36),
    Country.BLUE: (36, 92, 156),
    Country.GREEN: (36, 120, 64),
    Country.YELLOW: (196, 156, 28),
    Country.ORANGE: (196, 96, 28),
}

COUNTRY_HATCH = {
    Country.RED: "diag",
    Country.BLUE: "horiz",
    Country.GREEN: "dots",
    Country.YELLOW: "vert",
    Country.ORANGE: "diag2",
}

COUNTRY_SHORT = {
    Country.NONE: "—",
    Country.RED: "Rouge",
    Country.BLUE: "Bleu",
    Country.GREEN: "Vert",
    Country.YELLOW: "Jaune",
    Country.ORANGE: "Orange",
}

COUNTRY_NAMES = {
    Country.NONE: "Aucun",
    Country.RED: "Royaume Rouge",
    Country.BLUE: "Royaume Bleu",
    Country.GREEN: "Royaume Vert",
    Country.YELLOW: "Royaume Jaune",
    Country.ORANGE: "Royaume Orange",
}

TERRAIN_FULL_NAMES = {
    TerrainType.PLAIN: "Plaine",
    TerrainType.MOUNTAIN: "Montagne",
    TerrainType.FOREST: "Forêt",
    TerrainType.WATER: "Eau",
    TerrainType.BEACH: "Plage",
    TerrainType.BRIDGE: "Pont",
}

UI_BG_COLOR = (32, 34, 40)
UI_TEXT_COLOR = (220, 220, 220)
UI_TITLE_COLOR = (255, 255, 255)


class UnitType(Enum):
    SWORDSMAN = 0
    CROSSBOWMAN = 1
    CAVALRY = 2


UNIT_NAMES = {
    UnitType.SWORDSMAN: "Spadassin",
    UnitType.CROSSBOWMAN: "Arbalétrier",
    UnitType.CAVALRY: "Cavalerie",
}
UNIT_LETTERS = {
    UnitType.SWORDSMAN: "S",
    UnitType.CROSSBOWMAN: "A",
    UnitType.CAVALRY: "C",
}

UNIT_COSTS = {
    UnitType.SWORDSMAN: 40,
    UnitType.CROSSBOWMAN: 55,
    UnitType.CAVALRY: 70,
}
MAX_UNITS_PER_ARMY = 16
UNIT_UPKEEP = 5

CITY_COST = 150
CITY_INCOME = 50
CAPITAL_INCOME = 100
CITY_TERRITORY_REQUIREMENT = 25
BRIDGE_COST = 90
EMBARK_COST = 50
SHIP_MOVEMENT_RANGE = 5

UNIT_STATS = {
    UnitType.SWORDSMAN: {"attack": 3, "defense": 4},
    UnitType.CROSSBOWMAN: {"attack": 3, "defense": 2},
    UnitType.CAVALRY: {"attack": 4, "defense": 3},
}

MOVEMENT_RANGE = 3
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
    {"id": "engineering", "name": "Ingénierie", "cost": 280},
    {"id": "ballistics", "name": "Balistique", "cost": 320},
    {"id": "logistics", "name": "Logistique", "cost": 360},
]

FOG_RADIUS = 2

TERRAIN_DEFENSE_BONUS = {
    TerrainType.PLAIN: 0,
    TerrainType.MOUNTAIN: 2,
    TerrainType.FOREST: 1,
    TerrainType.WATER: 0,
    TerrainType.BEACH: 0,
    TerrainType.BRIDGE: 0,
}

KINGDOM_TRAITS = {
    Country.RED: {
        "id": "swords",
        "name": "Lames du Royaume",
        "blurb": "Spadassins moins chers et plus solides",
        "swordsman_cost_reduction": 10,
        "swordsman_attack_bonus": 1,
    },
    Country.BLUE: {
        "id": "navy",
        "name": "Maîtres des détroits",
        "blurb": "Ponts et transports moins chers",
        "bridge_cost_reduction": 30,
        "embark_cost_reduction": 20,
    },
    Country.GREEN: {
        "id": "woods",
        "name": "Seigneurs des forêts",
        "blurb": "Bonus défense en forêt, villes plus rentables",
        "forest_defense_bonus": 1,
        "city_income_bonus": 15,
    },
    Country.YELLOW: {
        "id": "gold",
        "name": "Trésor impérial",
        "blurb": "Les capitales rapportent plus d'or",
        "capital_income_bonus": 40,
    },
    Country.ORANGE: {
        "id": "cavalry",
        "name": "Cavaliers du vent",
        "blurb": "La cavalerie se déplace plus loin",
        "cavalry_move_bonus": 1,
    },
}
