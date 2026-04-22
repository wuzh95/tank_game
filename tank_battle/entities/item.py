from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pygame

from tank_battle import settings

ItemType = Literal["heal", "shield", "rapid_fire"]


@dataclass
class Item:
    item_type: ItemType
    position: pygame.math.Vector2
    lifetime: float = settings.ITEM_LIFETIME
    size: int = 20

    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.position.x - self.size / 2),
            int(self.position.y - self.size / 2),
            self.size,
            self.size,
        )

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface) -> None:
        color_map = {
            "heal": settings.COLOR_ITEM_HEAL,
            "shield": settings.COLOR_ITEM_SHIELD,
            "rapid_fire": settings.COLOR_ITEM_RAPID,
        }
        rect = self.rect()
        pygame.draw.rect(surface, color_map[self.item_type], rect, border_radius=4)
        pygame.draw.rect(surface, (30, 30, 30), rect, width=2, border_radius=4)

