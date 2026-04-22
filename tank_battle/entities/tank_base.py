from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

import pygame

Vec2 = pygame.math.Vector2


@dataclass
class TankBase:
    position: Vec2
    size: int
    speed: float
    hp: int
    direction: Vec2
    color: Tuple[int, int, int]

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.position.x - self.size / 2),
            int(self.position.y - self.size / 2),
            self.size,
            self.size,
        )

    def move(self, movement: Vec2, dt: float, blocked_rects: list[pygame.Rect]) -> None:
        if movement.length_squared() == 0:
            return
        move_dir = movement.normalize()
        if move_dir.length_squared() > 0:
            self.direction = move_dir
        delta = move_dir * self.speed * dt

        self.position.x += delta.x
        rect = self.get_rect()
        for blocker in blocked_rects:
            if rect.colliderect(blocker):
                if delta.x > 0:
                    self.position.x = blocker.left - self.size / 2
                else:
                    self.position.x = blocker.right + self.size / 2
                rect = self.get_rect()

        self.position.y += delta.y
        rect = self.get_rect()
        for blocker in blocked_rects:
            if rect.colliderect(blocker):
                if delta.y > 0:
                    self.position.y = blocker.top - self.size / 2
                else:
                    self.position.y = blocker.bottom + self.size / 2
                rect = self.get_rect()

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.get_rect()
        pygame.draw.rect(surface, self.color, rect)
        barrel_len = self.size * 0.65
        center = self.position
        barrel_end = (
            center.x + self.direction.x * barrel_len,
            center.y + self.direction.y * barrel_len,
        )
        pygame.draw.line(surface, (20, 20, 20), center, barrel_end, width=4)
        pygame.draw.circle(surface, (20, 20, 20), rect.center, int(self.size * 0.16))

    def is_dead(self) -> bool:
        return self.hp <= 0

    def angle(self) -> float:
        return math.degrees(math.atan2(-self.direction.y, self.direction.x))

