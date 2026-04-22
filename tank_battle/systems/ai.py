from __future__ import annotations

import random

import pygame

from tank_battle.entities.enemy import Enemy
from tank_battle.entities.player import Player


def update_enemy_behavior(
    enemy: Enemy,
    player: Player,
    dt: float,
    blocked_rects: list[pygame.Rect],
) -> None:
    enemy.update_timers(dt)
    to_player = player.position - enemy.position
    distance = to_player.length()

    if distance < 220:
        enemy.behavior.state = "chase"
    elif enemy.behavior.state_timer <= 0:
        enemy.behavior.state = "patrol"
        enemy.behavior.state_timer = random.uniform(1.2, 2.4)
        enemy.behavior.patrol_direction = pygame.Vector2(
            random.choice([-1, 0, 1]), random.choice([-1, 0, 1])
        )
        if enemy.behavior.patrol_direction.length_squared() == 0:
            enemy.behavior.patrol_direction = pygame.Vector2(0, 1)

    if enemy.behavior.state == "chase":
        movement = to_player.normalize() if distance > 1 else pygame.Vector2(0, 0)
    else:
        movement = enemy.behavior.patrol_direction
    old_pos = enemy.position.copy()
    enemy.move(movement, dt, blocked_rects)
    if (enemy.position - old_pos).length_squared() < 1e-3:
        enemy.behavior.patrol_direction = pygame.Vector2(
            random.choice([-1, 1]), random.choice([-1, 1])
        )

