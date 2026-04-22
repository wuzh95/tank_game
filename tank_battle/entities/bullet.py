from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pygame

from tank_battle import settings

OwnerType = Literal["player", "enemy"]


@dataclass
class Bullet:
    position: pygame.math.Vector2
    velocity: pygame.math.Vector2
    owner: OwnerType
    damage: int = settings.BULLET_DAMAGE
    radius: int = 4
    lifetime: float = settings.BULLET_LIFETIME

    def update(self, dt: float) -> bool:
        self.position += self.velocity * dt
        self.lifetime -= dt
        return self.lifetime > 0

    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.position.x - self.radius),
            int(self.position.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def draw(self, surface: pygame.Surface) -> None:
        color = (
            settings.COLOR_BULLET_PLAYER
            if self.owner == "player"
            else settings.COLOR_BULLET_ENEMY
        )
        pygame.draw.circle(surface, color, self.position, self.radius)

