from __future__ import annotations

import random

from tank_battle.entities.enemy import Enemy
from tank_battle.systems.level import LevelConfig


class EnemySpawner:
    def __init__(self, level: LevelConfig) -> None:
        self.level = level
        self.wave_index = 0
        self.remaining_in_wave = level.waves[0] if level.waves else 0
        self.spawn_timer = 0.0

    def update(self, dt: float, alive_count: int) -> list[Enemy]:
        self.spawn_timer -= dt
        spawned: list[Enemy] = []
        if self.remaining_in_wave <= 0:
            return spawned
        if alive_count >= self.level.max_on_field:
            return spawned
        if self.spawn_timer > 0:
            return spawned

        spawn_pos = random.choice(self.level.spawn_points).copy()
        enemy = Enemy(
            position=spawn_pos,
            speed=self.level.enemy_speed,
            hp=self.level.enemy_hp,
            shot_cooldown=self.level.enemy_shot_cooldown,
        )
        spawned.append(enemy)
        self.remaining_in_wave -= 1
        self.spawn_timer = random.uniform(0.8, 1.4)
        return spawned

    def on_wave_cleared(self) -> None:
        self.wave_index += 1
        if self.wave_index < len(self.level.waves):
            self.remaining_in_wave = self.level.waves[self.wave_index]

    def is_level_finished(self, alive_count: int) -> bool:
        completed_waves = self.wave_index >= len(self.level.waves) - 1
        return completed_waves and self.remaining_in_wave == 0 and alive_count == 0

