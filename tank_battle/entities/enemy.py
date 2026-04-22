from __future__ import annotations

import random
from dataclasses import dataclass, field

import pygame

from tank_battle import settings
from tank_battle.entities.bullet import Bullet
from tank_battle.entities.tank_base import TankBase


@dataclass
class EnemyBehavior:
    state: str = "patrol"
    state_timer: float = 0.0
    shoot_timer: float = 0.0
    patrol_direction: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 1))


class Enemy(TankBase):
    def __init__(
        self,
        position: pygame.math.Vector2,
        speed: float = settings.ENEMY_BASE_SPEED,
        hp: int = settings.ENEMY_BASE_HP,
        shot_cooldown: float = settings.ENEMY_SHOT_COOLDOWN,
    ) -> None:
        super().__init__(
            position=position,
            size=28,
            speed=speed,
            hp=hp,
            direction=pygame.Vector2(0, 1),
            color=settings.COLOR_ENEMY,
        )
        self.shot_cooldown = shot_cooldown
        self.behavior = EnemyBehavior(
            state_timer=random.uniform(1.2, 2.8),
            shoot_timer=random.uniform(0.4, self.shot_cooldown),
            patrol_direction=pygame.Vector2(random.choice([-1, 1]), 0),
        )

    def update_timers(self, dt: float) -> None:
        self.behavior.state_timer = max(0.0, self.behavior.state_timer - dt)
        self.behavior.shoot_timer = max(0.0, self.behavior.shoot_timer - dt)

    def try_shoot(self) -> Bullet | None:
        if self.behavior.shoot_timer > 0:
            return None
        self.behavior.shoot_timer = self.shot_cooldown
        if self.direction.length() > 0:
            direction = self.direction.normalize()
        else:
            direction = pygame.Vector2(0, 1)
        velocity = direction * settings.BULLET_SPEED * 0.85
        start_pos = self.position + direction * (self.size * 0.65)
        return Bullet(position=start_pos.copy(), velocity=velocity, owner="enemy")

