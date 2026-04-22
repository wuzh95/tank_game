from __future__ import annotations

import random

from tank_battle import settings
from tank_battle.entities.bullet import Bullet
from tank_battle.entities.enemy import Enemy
from tank_battle.entities.item import Item, ItemType
from tank_battle.entities.player import Player
from tank_battle.entities.wall import Wall


def resolve_bullet_collisions(
    bullets: list[Bullet],
    player: Player,
    enemies: list[Enemy],
    walls: list[Wall],
) -> tuple[list[Bullet], list[Enemy], list[Item], int]:
    survivors: list[Bullet] = []
    dead_enemies: list[Enemy] = []
    drops: list[Item] = []
    score_gain = 0

    for bullet in bullets:
        rect = bullet.rect()
        hit_wall = any(rect.colliderect(wall.rect) for wall in walls)
        if hit_wall:
            continue

        if bullet.owner == "enemy":
            if rect.colliderect(player.get_rect()):
                player.damage(bullet.damage)
                continue
            survivors.append(bullet)
            continue

        hit_enemy = False
        for enemy in enemies:
            if rect.colliderect(enemy.get_rect()):
                enemy.hp -= bullet.damage
                hit_enemy = True
                if enemy.is_dead():
                    dead_enemies.append(enemy)
                    score_gain += 100
                    if random.random() < settings.ITEM_DROP_CHANCE:
                        drops.append(Item(random_item_type(), enemy.position.copy()))
                break
        if not hit_enemy:
            survivors.append(bullet)

    dead_ids = {id(enemy) for enemy in dead_enemies}
    living_enemies = [e for e in enemies if id(e) not in dead_ids]
    return survivors, living_enemies, drops, score_gain


def resolve_item_pickups(items: list[Item], player: Player) -> tuple[list[Item], list[str]]:
    remaining: list[Item] = []
    events: list[str] = []
    for item in items:
        if item.rect().colliderect(player.get_rect()):
            if item.item_type == "heal":
                player.hp = min(settings.PLAYER_HP + 2, player.hp + 2)
                events.append("heal")
            elif item.item_type == "shield":
                player.shield_timer = settings.SHIELD_DURATION
                events.append("shield")
            elif item.item_type == "rapid_fire":
                player.rapid_fire_timer = settings.RAPID_FIRE_DURATION
                events.append("rapid_fire")
            continue
        remaining.append(item)
    return remaining, events


def random_item_type() -> ItemType:
    return random.choice(["heal", "shield", "rapid_fire"])

