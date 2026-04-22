from __future__ import annotations

import pygame

from tank_battle import settings
from tank_battle.entities.bullet import Bullet
from tank_battle.entities.tank_base import TankBase


class Player(TankBase):
    def __init__(self, position: pygame.math.Vector2) -> None:
        super().__init__(
            position=position,
            size=30,
            speed=settings.PLAYER_SPEED,
            hp=settings.PLAYER_HP,
            direction=pygame.Vector2(0, -1),
            color=settings.COLOR_PLAYER,
        )
        self.base_shot_cooldown = settings.PLAYER_SHOT_COOLDOWN
        self.shot_cooldown = settings.PLAYER_SHOT_COOLDOWN
        self.shot_timer = 0.0
        self.shield_timer = 0.0
        self.rapid_fire_timer = 0.0

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> pygame.math.Vector2:
        movement = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            movement.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            movement.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            movement.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            movement.x += 1
        return movement

    def try_shoot(self) -> Bullet | None:
        if self.shot_timer > 0:
            return None
        self.shot_timer = self.shot_cooldown
        velocity = self.direction.normalize() * settings.BULLET_SPEED
        start_pos = self.position + self.direction.normalize() * (self.size * 0.6)
        return Bullet(position=start_pos.copy(), velocity=velocity, owner="player")

    def update(self, dt: float) -> None:
        self.shot_timer = max(0.0, self.shot_timer - dt)
        self.shield_timer = max(0.0, self.shield_timer - dt)
        self.rapid_fire_timer = max(0.0, self.rapid_fire_timer - dt)
        self.shot_cooldown = (
            self.base_shot_cooldown * settings.RAPID_FIRE_MULTIPLIER
            if self.rapid_fire_timer > 0
            else self.base_shot_cooldown
        )

    def damage(self, value: int) -> None:
        if self.shield_timer > 0:
            return
        self.hp -= value

