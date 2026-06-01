"""Réglages persistants (volume, vitesse IA, difficulté)."""

import json
import os

SETTINGS_PATH = os.path.join("data", "settings.json")

DEFAULTS = {
    "tutorial_done": False,
    "volume": 0.7,
    "ai_speed": "normal",
    "difficulty": "normal",
}

AI_SPEED_DELAYS_MS = {
    "instant": 0,
    "fast": 350,
    "normal": 1000,
    "slow": 2200,
}

DIFFICULTY_CONFIG = {
    "easy": {
        "human_gold": 850,
        "ai_gold": 280,
        "ai_recruit_limit": 1,
        "ai_truce_turns": 5,
    },
    "normal": {
        "human_gold": 700,
        "ai_gold": 350,
        "ai_recruit_limit": 2,
        "ai_truce_turns": 3,
    },
    "hard": {
        "human_gold": 520,
        "ai_gold": 480,
        "ai_recruit_limit": 3,
        "ai_truce_turns": 1,
    },
}


def load_settings():
    data = dict(DEFAULTS)
    if not os.path.exists(SETTINGS_PATH):
        return data
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            stored = json.load(f)
        data.update({k: stored[k] for k in DEFAULTS if k in stored})
    except (json.JSONDecodeError, OSError):
        pass
    return data


def save_settings(data):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    merged = dict(DEFAULTS)
    merged.update(data)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
    return merged


def cycle_value(current, options):
    if current not in options:
        return options[0]
    idx = (options.index(current) + 1) % len(options)
    return options[idx]
