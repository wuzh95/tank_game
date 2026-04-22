from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pygame

from tank_battle import settings
from tank_battle.entities.wall import Wall


@dataclass
class LevelConfig:
    name: str
    waves: list[int]
    enemy_speed: float
    enemy_hp: int
    enemy_shot_cooldown: float
    max_on_field: int
    spawn_points: list[pygame.Vector2]
    player_spawn: pygame.Vector2
    walls: list[Wall]


def _tile_to_rect(tx: int, ty: int) -> pygame.Rect:
    return pygame.Rect(
        tx * settings.TILE_SIZE,
        ty * settings.TILE_SIZE,
        settings.TILE_SIZE,
        settings.TILE_SIZE,
    )


def load_levels(path: Path) -> list[LevelConfig]:
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    levels: list[LevelConfig] = []
    for level_data in raw["levels"]:
        walls = [Wall(_tile_to_rect(p[0], p[1])) for p in level_data["walls"]]
        spawn_points = [pygame.Vector2(x, y) for x, y in level_data["spawn_points"]]
        config = LevelConfig(
            name=level_data["name"],
            waves=list(level_data["waves"]),
            enemy_speed=float(level_data["enemy_speed"]),
            enemy_hp=int(level_data["enemy_hp"]),
            enemy_shot_cooldown=float(level_data["enemy_shot_cooldown"]),
            max_on_field=int(level_data.get("max_on_field", settings.MAX_ENEMIES_ON_FIELD)),
            spawn_points=spawn_points,
            player_spawn=pygame.Vector2(*level_data["player_spawn"]),
            walls=walls,
        )
        levels.append(config)
    return levels

