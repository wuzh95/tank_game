from __future__ import annotations

from dataclasses import dataclass

import pygame

from tank_battle import settings


@dataclass
class Wall:
    rect: pygame.Rect

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, settings.COLOR_WALL, self.rect)
        pygame.draw.rect(surface, (92, 67, 43), self.rect, width=2)

