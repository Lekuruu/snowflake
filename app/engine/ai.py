
from __future__ import annotations
from typing import Callable, Iterable

from twisted.internet.address import IPv4Address
from twisted.internet import reactor

from app.engine.penguin import Penguin
from app.objects.ninjas import Ninja
from app.objects.enemies import Enemy
from app.objects import GameObject

import logging
import random
import config


def delay(minimum: int | float, maximum: int | float) -> Callable:
    def decorator(func: Callable) -> Callable:
        return lambda *args, **kwargs: reactor.callLater(
            random.uniform(minimum, maximum),  # type: ignore
            func, *args, **kwargs
        )
    return decorator

def manhatten_distance(x1: int, y1: int, x2: int, y2: int) -> int | float:
    return abs(x1 - x2) + abs(y1 - y2)


class PenguinAI(Penguin):
    def __init__(
        self,
        server,
        element: str,
        battle_mode: int
    ) -> None:
        super().__init__(server, IPv4Address('TCP', '127.0.0.1', 69420))

        self.logger = logging.getLogger(f'AI ({element.capitalize()})')
        self.object = server.data.fetch_random_penguin()
        assert self.object is not None, "The data provider has no penguin for AI players"

        self.name = self.object.nickname
        self.element = element
        self.battle_mode = battle_mode
        self.pid = -1
        self.in_queue = True
        self.is_ready = True
        self.logged_in = True
        self.is_bot = True

    @delay(0.25, 2)
    def confirm_move(self) -> None:
        if self.is_ready:
            return

        confirm = GameObject(
            self.game,
            'ui_confirm',
            x_offset=0.5,
            y_offset=1.05
        )

        confirm.x = self.ninja.x
        confirm.y = self.ninja.y
        confirm.place_object()
        confirm.place_sprite(confirm.name)
        confirm.play_sound('SFX_MG_2013_CJSnow_UIPlayerReady_VBR8')
        self.is_ready = True

    @delay(0.5, 3)
    def select_move(self) -> None:
        # Check for k.o. state
        if self.ninja.hp <= 0:
            if not self.member_card:
                # k.o and no member card availabe :(
                return

            self.member_card.place()
            return

        # Check for k.o. allies
        for ninja in self.game.ninjas:
            if not ninja.hp <= 0:
                continue

            if ninja.client.member_card:
                continue

            if self.is_ninja_getting_revived(ninja):
                continue

            if not self.can_heal_ninja(ninja):
                continue

            # We have an ally to revive!
            self.select_target(ninja.grid_x, ninja.grid_y)
            self.confirm_move()
            return

        actions = {
            'snow': self.snow_actions,
            'water': self.water_actions,
            'fire': self.fire_actions
        }
        actions[self.element]()
        self.confirm_move()

    def select_target(self, x: int, y: int) -> None:
        target = next(
            (target for target in self.ninja.targets
            if target.x == x and target.y == y),
            None
        )

        if not target:
            return

        target.select()

    def snow_actions(self) -> None:
        # Snow should keep a distance from all enemies
        # and focus on healing their allies
        injured_allies = [
            ninja for ninja in self.game.ninjas
            if ninja != self.ninja
            and ninja.hp > 0
            and ninja.hp < ninja.max_hp
            and not ninja.client.disconnected
        ]

        if injured_allies:
            move, target = self.best_move_for_heal(injured_allies)

            if move:
                self.place_ghost(move)

            if target:
                self.select_target(target.grid_x, target.grid_y)
                return

            # If we can't heal yet, move closer to injured allies so we can next turn
            move = self.best_move_toward_allies(injured_allies)

            if move:
                self.place_ghost(move)
                return

        living_enemies = self.living_enemies()

        if not living_enemies:
            return

        # If no ally needs heals, snow attacks while staying as far as possible
        move, target = self.best_move_for_attack(
            living_enemies,
            prefer_closest=False,
            prefer_far_from_enemies=True
        )

        if move:
            self.place_ghost(move)

        if target:
            self.select_target(target.grid_x, target.grid_y)
            return

        move = self.best_positioning_tile(prefer_far=True)

        if move:
            self.place_ghost(move)

    def fire_actions(self) -> None:
        # Fire should keep a distance from all enemies
        # and focus on attacking their enemies
        living_enemies = self.living_enemies()

        if not living_enemies:
            return

        move, target = self.best_move_for_attack(
            living_enemies,
            prefer_closest=False,
            prefer_far_from_enemies=True
        )

        if move:
            self.place_ghost(move)

        if target:
            self.select_target(target.grid_x, target.grid_y)
            return

        # We can't attack :(
        # Find a fallback position to go to
        move = self.best_standoff_tile(self.ninja.range)

        if move:
            self.place_ghost(move)

    def water_actions(self) -> None:
        # Water needs to move as close as possible to their
        # enemies and focus on attacking them
        living_enemies = self.living_enemies()

        if not living_enemies:
            return

        move, target = self.best_move_for_attack(
            living_enemies,
            prefer_closest=True,
            prefer_far_from_enemies=False
        )

        if move:
            self.place_ghost(move)

        if target:
            self.select_target(target.grid_x, target.grid_y)
            return

        move = self.best_positioning_tile(prefer_far=False)

        if move:
            self.place_ghost(move)

    def best_enemy_target(
        self,
        targets: list[GameObject],
        from_tile: GameObject,
        prefer_closest: bool
    ) -> GameObject | None:
        enemies = [
            self.game.grid[target.grid_x, target.grid_y]
            for target in targets
        ]
        enemies = [enemy for enemy in enemies if isinstance(enemy, Enemy)]

        if not enemies:
            return None

        def score(enemy: Enemy):
            distance = manhatten_distance(
                enemy.grid_x,
                enemy.grid_y,
                from_tile.grid_x,
                from_tile.grid_y
            )

            if prefer_closest:
                return (enemy.hp, distance)

            return (enemy.hp, -distance)

        enemy = min(enemies, key=score)

        return self.game.grid.get_tile(
            enemy.grid_x,
            enemy.grid_y
        )

    def best_move_for_attack(
        self,
        enemies: list[Enemy],
        prefer_closest: bool,
        prefer_far_from_enemies: bool
    ) -> tuple[GameObject | None, GameObject | None]:
        best_move = None
        best_score = None
        best_targets = []

        for tile in self.available_tiles():
            targets = list(self.ninja.attackable_tiles(tile.grid_x, tile.grid_y))

            if not targets:
                continue

            nearest_enemy = self.nearest_enemy_distance(tile, enemies)
            attack_count = len(targets)

            score = (
                attack_count,
                -nearest_enemy if prefer_closest else nearest_enemy
            )

            if best_score is None or score > best_score:
                best_move = tile
                best_score = score
                best_targets = targets

        if best_move is None:
            # Either no attack candidates or no move picked
            return None, None

        # Select what enemy to attack if we have multiple
        target = self.best_enemy_target(
            best_targets, best_move,
            prefer_closest=(not prefer_far_from_enemies)
        )
        return best_move, target

    def best_move_for_heal(self, allies: list[Ninja]) -> tuple[GameObject | None, GameObject | None]:
        best_move = None
        best_score = None
        best_target = None

        for tile in self.available_tiles():
            heal_tiles = list(self.ninja.healable_tiles(tile.grid_x, tile.grid_y))

            if not heal_tiles:
                continue

            for heal_tile in heal_tiles:
                ally = self.game.grid[heal_tile.grid_x, heal_tile.grid_y]

                if not isinstance(ally, Ninja):
                    continue

                missing_hp = ally.max_hp - ally.hp
                score = (1, missing_hp)

                if ally.hp <= 0:
                    # Prioritize revives above regular heals
                    score = (2, 0)

                if best_score is None or score > best_score:
                    best_move = tile
                    best_score = score
                    best_target = heal_tile

        return best_move, best_target

    def best_standoff_tile(self, target_distance: int) -> GameObject | None:
        """Choose a tile that keeps the ninja near the given distance from enemies"""
        enemies = self.living_enemies()

        if not enemies:
            return None

        tiles = self.available_tiles()

        if not tiles:
            return None

        current_tile = self.game.grid[self.ninja.grid_x, self.ninja.grid_y]

        # Prefer tiles that get closer to the desired standoff distance
        # On ties, keep a little extra distance for safer positioning
        best_tile = min(
            tiles,
            key=lambda tile: (
                abs(self.nearest_enemy_distance(tile, enemies) - target_distance),
                -self.nearest_enemy_distance(tile, enemies),
                0 if (current_tile and tile != current_tile) else 1
            )
        )
        return best_tile

    def best_positioning_tile(self, prefer_far: bool) -> GameObject | None:
        """Choose the available tile nearest / farthest from the closest enemy"""
        enemies = self.living_enemies()

        if not enemies:
            return None

        tiles = self.available_tiles()

        if not tiles:
            return None

        key = (
            (lambda tile: self.nearest_enemy_distance(tile, enemies)) if prefer_far else
            (lambda tile: -self.nearest_enemy_distance(tile, enemies))
        )
        best_tile = max(tiles, key=key)
        return best_tile

    def best_move_toward_allies(self, allies: list[Ninja]) -> GameObject | None:
        """Move snow ninja closer to injured allies to improve heal reach next turn"""
        if not allies:
            return None

        tiles = self.available_tiles()

        if not tiles:
            return None

        current_tile = self.game.grid[self.ninja.grid_x, self.ninja.grid_y]

        # Prefer tiles that reduce average distance to allies
        # On ties, prefer moving over staying
        best_tile = min(
            tiles,
            key=lambda tile: (
                sum(manhatten_distance(tile.grid_x, tile.grid_y, ally.grid_x, ally.grid_y) for ally in allies) / len(allies),
                0 if (current_tile and tile != current_tile) else 1
            )
        )
        return best_tile

    def place_ghost(self, tile: GameObject) -> None:
        if tile.x == self.ninja.x and tile.y == self.ninja.y:
            # Already placed the ghost here
            return

        self.ninja.place_ghost(tile.grid_x, tile.grid_y)

    def living_enemies(self) -> list[Enemy]:
        return [
            enemy for enemy in self.game.enemies
            if enemy.hp > 0
        ]

    def available_tiles(self) -> list[GameObject]:
        current_tile = self.game.grid[self.ninja.grid_x, self.ninja.grid_y]
        tiles = list(self.ninja.movable_tiles())

        if current_tile:
            tiles.append(current_tile)

        return tiles

    def nearest_enemy_distance(self, tile: GameObject, enemies: Iterable[Enemy]) -> int | float:
        return min(
            manhatten_distance(
                tile.grid_x, tile.grid_y,
                enemy.grid_x, enemy.grid_y
            )
            for enemy in enemies
        )

    def is_ninja_getting_revived(self, ninja: Ninja) -> bool:
        for ninja in self.game.ninjas:
            if ninja.selected_object == ninja:
                return True

        return False

    def can_heal_ninja(self, target: Ninja) -> bool:
        tiles = self.game.grid.surrounding_tiles(
            target.grid_x,
            target.grid_y
        )

        for tile in tiles:
            can_move = self.game.grid.can_move_to_tile(
                self.ninja,
                tile.grid_x,
                tile.grid_y
            )

            if not can_move:
                continue

            self.ninja.place_ghost(tile.grid_x, tile.grid_y)
            return True

        current_tile = self.game.grid[self.ninja.grid_x, self.ninja.grid_y]

        if current_tile in tiles:
            return True

        return False

    def unlock_stamp(self, id: int) -> None:
        # Bots don't have an account for stamps
        pass
