"""Sauvegarde et chargement de parties (JSON)."""

import json
import os
from constants import *
from cell import Cell
from army import Army
from player import Player

SAVE_VERSION = 2
SAVE_DIR = "saves"
SAVE_PATH = os.path.join(SAVE_DIR, "latest.json")


def _enum_name(value):
    return value.name if hasattr(value, "name") else str(value)


def _enum_from_name(enum_cls, name):
    return enum_cls[name]


def _serialize_army(army):
    if army is None:
        return None
    return {
        "country": _enum_name(army.country),
        "unit_type": _enum_name(army.unit_type),
        "count": army.count,
        "has_moved": army.has_moved,
        "movement_left": army.movement_left,
        "is_fortified": army.is_fortified,
        "embarked": bool(getattr(army, "embarked", False)),
    }


def _deserialize_army(data):
    if data is None:
        return None
    army = Army(
        _enum_from_name(Country, data["country"]),
        _enum_from_name(UnitType, data["unit_type"]),
        data["count"],
    )
    army.has_moved = data["has_moved"]
    army.movement_left = data["movement_left"]
    army.is_fortified = data["is_fortified"]
    army.embarked = data.get("embarked", False)
    return army


def save_game(game):
    os.makedirs(SAVE_DIR, exist_ok=True)
    grid_data = []
    for x in range(GRID_COLS):
        col = []
        for y in range(GRID_ROWS):
            cell = game.grid[x][y]
            col.append(
                {
                    "terrain": _enum_name(cell.terrain),
                    "country": _enum_name(cell.country),
                    "is_capital": cell.is_capital,
                    "is_city": cell.is_city,
                    "bridge_hp": cell.bridge_hp,
                    "capital_owner": _enum_name(cell.capital_owner),
                    "city_owner": _enum_name(cell.city_owner),
                    "last_recruit_turn": cell.last_recruit_turn,
                    "discovered_by": [_enum_name(c) for c in cell.discovered_by],
                    "army": _serialize_army(cell.army),
                }
            )
        grid_data.append(col)

    players_data = {}
    for country, player in game.players.items():
        players_data[_enum_name(country)] = {
            "gold": player.gold,
            "is_ai": player.is_ai,
            "unlocked_techs": list(player.unlocked_techs),
            "city_income_bonus": player.city_income_bonus,
            "bridge_hp_bonus": player.bridge_hp_bonus,
            "bridge_cost_reduction": player.bridge_cost_reduction,
            "ranged_range_bonus": player.ranged_range_bonus,
            "ranged_damage_bonus": player.ranged_damage_bonus,
            "upkeep_reduction": player.upkeep_reduction,
            "swordsman_cost_reduction": getattr(player, "swordsman_cost_reduction", 0),
            "swordsman_attack_bonus": getattr(player, "swordsman_attack_bonus", 0),
            "embark_cost_reduction": getattr(player, "embark_cost_reduction", 0),
            "forest_defense_bonus": getattr(player, "forest_defense_bonus", 0),
            "capital_income_bonus": getattr(player, "capital_income_bonus", 0),
            "cavalry_move_bonus": getattr(player, "cavalry_move_bonus", 0),
        }

    payload = {
        "version": SAVE_VERSION,
        "game_mode": game.game_mode,
        "turn_number": game.turn_number,
        "current_player_country": _enum_name(game.current_player_country),
        "winner_country": _enum_name(game.winner_country) if game.winner_country else None,
        "player_defeated": game.player_defeated,
        "game_over_message": game.game_over_message,
        "defeated_countries": [_enum_name(c) for c in game.defeated_countries],
        "last_aggressor": {_enum_name(k): _enum_name(v) for k, v in game.last_aggressor.items()},
        "map_seed": getattr(game, "map_seed", None),
        "last_income": game.last_income,
        "last_upkeep": game.last_upkeep,
        "event_log": list(game.event_log),
        "gold_looted": {_enum_name(k): v for k, v in getattr(game, "gold_looted", {}).items()},
        "settings": dict(getattr(game, "settings", {})),
        "players": players_data,
        "grid": grid_data,
    }
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return True


def load_game(game):
    if not os.path.exists(SAVE_PATH):
        return False
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            payload = json.load(f)
        if payload.get("version") != SAVE_VERSION:
            return False
        return _apply_payload(game, payload)
    except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError) as err:
        print(f"Chargement impossible: {err}")
        return False


def _apply_payload(game, payload):
    game.state = "playing"
    game.game_mode = payload["game_mode"]
    game.turn_number = payload["turn_number"]
    game.current_player_country = _enum_from_name(Country, payload["current_player_country"])
    game.winner_country = (
        _enum_from_name(Country, payload["winner_country"]) if payload["winner_country"] else None
    )
    game.player_defeated = payload.get("player_defeated", False)
    game.game_over_message = payload.get("game_over_message", "")
    game.defeated_countries = {_enum_from_name(Country, n) for n in payload.get("defeated_countries", [])}
    game.last_aggressor = {
        _enum_from_name(Country, k): _enum_from_name(Country, v)
        for k, v in payload.get("last_aggressor", {}).items()
    }
    game.map_seed = payload.get("map_seed")
    game.last_income = payload.get("last_income", 0)
    game.last_upkeep = payload.get("last_upkeep", 0)
    game.event_log = payload.get("event_log", [])
    game.gold_looted = {
        _enum_from_name(Country, k): v for k, v in payload.get("gold_looted", {}).items()
    }
    from settings import load_settings, DIFFICULTY_CONFIG

    game.settings = payload.get("settings") or load_settings()
    if hasattr(game, "audio") and game.audio:
        game.audio.set_volume(game.settings.get("volume", 0.7))
    game.difficulty_cfg = DIFFICULTY_CONFIG.get(
        game.settings.get("difficulty", "normal"), DIFFICULTY_CONFIG["normal"]
    )
    if hasattr(game, "pause_menu") and game.pause_menu:
        game.pause_menu.settings = game.settings
        game.pause_menu.close()

    game.grid = [[Cell(x, y) for y in range(GRID_ROWS)] for x in range(GRID_COLS)]
    for x in range(GRID_COLS):
        for y in range(GRID_ROWS):
            data = payload["grid"][x][y]
            cell = game.grid[x][y]
            cell.terrain = _enum_from_name(TerrainType, data["terrain"])
            cell.country = _enum_from_name(Country, data["country"])
            cell.is_capital = data["is_capital"]
            cell.is_city = data["is_city"]
            cell.bridge_hp = data.get("bridge_hp", 0)
            cell.capital_owner = _enum_from_name(Country, data["capital_owner"])
            cell.city_owner = _enum_from_name(Country, data["city_owner"])
            cell.last_recruit_turn = data.get("last_recruit_turn", -1)
            cell.discovered_by = {_enum_from_name(Country, n) for n in data.get("discovered_by", [])}
            cell.army = _deserialize_army(data.get("army"))

    game.players = {}
    for name, pdata in payload["players"].items():
        country = _enum_from_name(Country, name)
        player = Player(country)
        player.gold = pdata["gold"]
        player.is_ai = pdata["is_ai"]
        player.unlocked_techs = list(pdata.get("unlocked_techs", []))
        player.city_income_bonus = pdata.get("city_income_bonus", player.city_income_bonus)
        player.bridge_hp_bonus = pdata.get("bridge_hp_bonus", 0)
        player.bridge_cost_reduction = pdata.get("bridge_cost_reduction", player.bridge_cost_reduction)
        player.ranged_range_bonus = pdata.get("ranged_range_bonus", 0)
        player.ranged_damage_bonus = pdata.get("ranged_damage_bonus", 0)
        player.upkeep_reduction = pdata.get("upkeep_reduction", 0)
        player.swordsman_cost_reduction = pdata.get("swordsman_cost_reduction", player.swordsman_cost_reduction)
        player.swordsman_attack_bonus = pdata.get("swordsman_attack_bonus", player.swordsman_attack_bonus)
        player.embark_cost_reduction = pdata.get("embark_cost_reduction", player.embark_cost_reduction)
        player.forest_defense_bonus = pdata.get("forest_defense_bonus", player.forest_defense_bonus)
        player.capital_income_bonus = pdata.get("capital_income_bonus", player.capital_income_bonus)
        player.cavalry_move_bonus = pdata.get("cavalry_move_bonus", player.cavalry_move_bonus)
        game.players[country] = player

    game.selected_cell = None
    game.selected_army_cell = None
    game.move_targets = set()
    game.attack_targets = set()
    game.ranged_targets = set()
    game.bridge_mode = False
    game.bridge_targets = set()
    game.ranged_mode = False
    game.preview_path_cells = []
    game.occupation_tracker = {}
    game.ai_turn_pending = False
    game.ai_turn_resume_at = 0
    game.animations = []
    game.visibility = set()
    game.disembark_targets = set()
    game.embark_targets = set()
    from fx import Effects

    if not getattr(game, "fx", None):
        game.fx = Effects()
    else:
        game.fx.clear()

    from ui import UI
    from ai import AI

    game.ui = UI(game.screen)
    game.ai = AI(game)
    return True
