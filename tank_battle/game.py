from __future__ import annotations

import enum
import math
from array import array
from dataclasses import dataclass

import pygame

from tank_battle import settings
from tank_battle.entities.bullet import Bullet
from tank_battle.entities.item import Item
from tank_battle.entities.player import Player
from tank_battle.entities.tank_base import TankBase
from tank_battle.systems.ai import update_enemy_behavior
from tank_battle.systems.collision import resolve_bullet_collisions, resolve_item_pickups
from tank_battle.systems.level import LevelConfig, load_levels
from tank_battle.systems.spawn import EnemySpawner


class GameState(enum.Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    WIN = "win"
    GAME_OVER = "game_over"


@dataclass
class AudioManager:
    enabled: bool = False

    def __post_init__(self) -> None:
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1)
            self.enabled = True
            self._build_sounds()
        except pygame.error:
            self.enabled = False

    def _build_sounds(self) -> None:
        self.sounds["shoot"] = self._tone(780, 0.07, 0.5)
        self.sounds["enemy_shoot"] = self._tone(520, 0.08, 0.4)
        self.sounds["explosion"] = self._tone(160, 0.2, 0.6)
        self.sounds["drop"] = self._tone(680, 0.1, 0.45)
        self.sounds["heal"] = self._tone(920, 0.11, 0.4)
        self.sounds["shield"] = self._tone(440, 0.14, 0.35)
        self.sounds["rapid_fire"] = self._tone(1040, 0.1, 0.35)
        self.sounds["lose"] = self._tone(210, 0.35, 0.55)

    def _tone(self, freq: int, duration: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        data = array("h")
        amp = int(32767 * max(0.0, min(1.0, volume)))
        for i in range(n_samples):
            t = i / sample_rate
            env = max(0.0, 1.0 - (i / max(1, n_samples)))
            sample = int(amp * env * math.sin(2 * math.pi * freq * t))
            data.append(sample)
        return pygame.mixer.Sound(buffer=data.tobytes())

    def play(self, event: str) -> None:
        if not self.enabled:
            return
        sound = self.sounds.get(event)
        if sound:
            sound.play()


class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption(settings.TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(settings.FONT_NAME, 24)
        self.small_font = pygame.font.SysFont(settings.FONT_NAME, 18)
        self.audio = AudioManager()

        self.levels = load_levels(settings.LEVELS_FILE)
        self.state = GameState.MENU
        self.running = True
        self.score = 0
        self.level_index = 0

        self.player = Player(pygame.Vector2(settings.SCREEN_WIDTH / 2, settings.SCREEN_HEIGHT - 64))
        self.spawner: EnemySpawner | None = None
        self.current_level: LevelConfig | None = None
        self.enemies = []
        self.bullets: list[Bullet] = []
        self.items: list[Item] = []
        self.flash_message = ""
        self.flash_timer = 0.0

    def start_game(self) -> None:
        self.score = 0
        self.level_index = 0
        self._load_level(self.level_index, reset_player=True)
        self.state = GameState.PLAYING

    def _load_level(self, idx: int, reset_player: bool = False) -> None:
        self.current_level = self.levels[idx]
        self.spawner = EnemySpawner(self.current_level)
        if reset_player:
            self.player = Player(self.current_level.player_spawn.copy())
        else:
            self.player.position = self.current_level.player_spawn.copy()
            self.player.direction = pygame.Vector2(0, -1)
        self.enemies.clear()
        self.bullets.clear()
        self.items.clear()
        self.flash_message = f"Level {idx + 1}: {self.current_level.name}"
        self.flash_timer = 2.0

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(settings.FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                if event.key == pygame.K_r and self.state in {GameState.GAME_OVER, GameState.WIN}:
                    self.start_game()
                if event.key == pygame.K_RETURN and self.state == GameState.MENU:
                    self.start_game()
                if event.key == pygame.K_SPACE and self.state == GameState.PLAYING:
                    bullet = self.player.try_shoot()
                    if bullet:
                        self.audio.play("shoot")
                        self.bullets.append(bullet)

    def _update(self, dt: float) -> None:
        self.flash_timer = max(0.0, self.flash_timer - dt)
        if self.state != GameState.PLAYING:
            return

        level = self.current_level
        spawner = self.spawner
        if not level or not spawner:
            return

        keys = pygame.key.get_pressed()
        movement = self.player.handle_input(keys)
        blockers = self._blocked_rects()
        self.player.move(movement, dt, blockers)
        self._clamp_entity(self.player)
        self.player.update(dt)

        spawned = spawner.update(dt, len(self.enemies))
        self.enemies.extend(spawned)

        for enemy in self.enemies:
            update_enemy_behavior(enemy, self.player, dt, blockers)
            self._clamp_entity(enemy)
            if self._enemy_can_shoot_player(enemy):
                bullet = enemy.try_shoot()
                if bullet:
                    self.audio.play("enemy_shoot")
                    self.bullets.append(bullet)

        self.bullets = [b for b in self.bullets if b.update(dt)]
        self.bullets = [b for b in self.bullets if self._in_bounds(b.position)]

        self.bullets, self.enemies, drops, score_gain = resolve_bullet_collisions(
            self.bullets, self.player, self.enemies, level.walls
        )
        if drops:
            self.audio.play("drop")
            self.items.extend(drops)
        if score_gain:
            self.audio.play("explosion")
            self.score += score_gain

        self.items = [item for item in self.items if item.update(dt)]
        self.items, pickup_events = resolve_item_pickups(self.items, self.player)
        for event_name in pickup_events:
            self.audio.play(event_name)

        if (
            spawner.remaining_in_wave == 0
            and not self.enemies
            and spawner.wave_index < len(level.waves) - 1
        ):
            spawner.on_wave_cleared()
            self.flash_message = f"Wave {spawner.wave_index + 1}"
            self.flash_timer = 1.5

        if spawner.is_level_finished(len(self.enemies)):
            if self.level_index < len(self.levels) - 1:
                self.level_index += 1
                self._load_level(self.level_index)
            else:
                self.state = GameState.WIN
                self.flash_message = "You Win! Press R to Restart"
                self.flash_timer = 999

        if self.player.is_dead():
            self.state = GameState.GAME_OVER
            self.flash_message = "Game Over! Press R to Restart"
            self.flash_timer = 999
            self.audio.play("lose")

    def _blocked_rects(self) -> list[pygame.Rect]:
        level = self.current_level
        if not level:
            return []
        return [wall.rect for wall in level.walls]

    def _clamp_entity(self, tank: TankBase) -> None:
        half = tank.size / 2
        tank.position.x = max(half, min(settings.SCREEN_WIDTH - half, tank.position.x))
        tank.position.y = max(half, min(settings.SCREEN_HEIGHT - half, tank.position.y))

    def _in_bounds(self, pos: pygame.Vector2) -> bool:
        return 0 <= pos.x <= settings.SCREEN_WIDTH and 0 <= pos.y <= settings.SCREEN_HEIGHT

    def _enemy_can_shoot_player(self, enemy) -> bool:
        to_player = self.player.position - enemy.position
        distance = to_player.length()
        if distance <= 1:
            return False
        direction = to_player.normalize()
        facing_score = enemy.direction.dot(direction)
        return distance < 320 and facing_score > 0.75

    def _draw_grid(self) -> None:
        self.screen.fill(settings.COLOR_BG)
        for x in range(0, settings.SCREEN_WIDTH, settings.TILE_SIZE):
            pygame.draw.line(self.screen, settings.COLOR_GRID, (x, 0), (x, settings.SCREEN_HEIGHT))
        for y in range(0, settings.SCREEN_HEIGHT, settings.TILE_SIZE):
            pygame.draw.line(self.screen, settings.COLOR_GRID, (0, y), (settings.SCREEN_WIDTH, y))

    def _draw_hud(self) -> None:
        level_name = self.current_level.name if self.current_level else "-"
        text = (
            f"HP:{self.player.hp}  Score:{self.score}  "
            f"Level:{self.level_index + 1}({level_name})  Enemies:{len(self.enemies)}"
        )
        label = self.small_font.render(text, True, settings.COLOR_TEXT)
        self.screen.blit(label, (8, 8))

        buff = []
        if self.player.shield_timer > 0:
            buff.append(f"Shield {math.ceil(self.player.shield_timer)}s")
        if self.player.rapid_fire_timer > 0:
            buff.append(f"Rapid {math.ceil(self.player.rapid_fire_timer)}s")
        if buff:
            buff_label = self.small_font.render(" | ".join(buff), True, settings.COLOR_TEXT)
            self.screen.blit(buff_label, (8, 34))

    def _draw_overlay(self, title: str, subtitle: str) -> None:
        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        t = self.font.render(title, True, settings.COLOR_TEXT)
        s = self.small_font.render(subtitle, True, settings.COLOR_TEXT)
        self.screen.blit(t, (settings.SCREEN_WIDTH / 2 - t.get_width() / 2, 260))
        self.screen.blit(s, (settings.SCREEN_WIDTH / 2 - s.get_width() / 2, 300))

    def _draw(self) -> None:
        self._draw_grid()
        if self.current_level:
            for wall in self.current_level.walls:
                wall.draw(self.screen)
        for item in self.items:
            item.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        self.player.draw(self.screen)
        if self.player.shield_timer > 0:
            pygame.draw.circle(
                self.screen,
                settings.COLOR_ITEM_SHIELD,
                self.player.position,
                22,
                width=2,
            )

        self._draw_hud()
        if self.flash_timer > 0 and self.flash_message:
            msg = self.font.render(self.flash_message, True, settings.COLOR_TEXT)
            self.screen.blit(msg, (settings.SCREEN_WIDTH / 2 - msg.get_width() / 2, 56))

        if self.state == GameState.MENU:
            self._draw_overlay("Tank Battle", "Press Enter to Start")
        elif self.state == GameState.PAUSED:
            self._draw_overlay("Paused", "Press Esc to Continue")
        elif self.state == GameState.GAME_OVER:
            self._draw_overlay("Game Over", "Press R to Restart")
        elif self.state == GameState.WIN:
            self._draw_overlay("Victory", "Press R to Restart")

        pygame.display.flip()

