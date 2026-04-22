from __future__ import annotations

import pygame

from tank_battle.game import Game


def main() -> None:
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()

