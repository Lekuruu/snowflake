
from __future__ import annotations
from typing import Callable, Iterable

from twisted.internet.address import IPv4Address
from twisted.internet import reactor

from app.engine.penguin import Penguin
from app.objects.ninjas import Ninja
from app.objects import GameObject
from app.objects.enemies import Enemy
from app.data import penguins

import logging
import random
import config

def delay(minimum: int, maximum: int) -> Callable:
    def decorator(func: Callable) -> Callable:
        return lambda *args, **kwargs: reactor.callLater(
            random.uniform(minimum, maximum),
            func, *args, **kwargs
        )
    return decorator

class PenguinAI(Penguin):
    def __init__(
        self,
        server,
        element: str,
        battle_mode: int
    ) -> None:
        super().__init__(server, IPv4Address('TCP', '127.0.0.1', 69420))
        self.logger = logging.getLogger(f'AI ({element.capitalize()})')
        self.object = penguins.fetch_random()
        self.name = self.object.nickname
        self.element = element
        self.battle_mode = battle_mode
        self.pid = -1
        self.in_queue = True
        self.is_ready = True
        self.logged_in = True
        self.is_bot = True

    def debug(self, message: str) -> None:
        if not config.ENABLE_NINJA_AI_DEBUG_LOGGING:
            return

        self.logger.info(message)

    def tile_debug(self, tile: GameObject | None) -> str:
        if tile is None:
            return 'None'

        return f'({tile.x},{tile.y})'

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
        self.debug(
            f'select_move start: pos=({self.ninja.x},{self.ninja.y}) '
            f'hp={self.ninja.hp}/{self.ninja.max_hp}'
        )

        # Check for k.o. state
        if self.ninja.hp <= 0:
            if not self.member_card:
                self.debug('ninja is KO and has no member card, confirming move')
                self.confirm_move()
                return

            self.debug('ninja is KO and uses member card revive')
            self.member_card.place()
            self.confirm_move()
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

            self.debug(f'revive target selected: ({ninja.x},{ninja.y})')
            self.select_target(ninja.x, ninja.y)
            self.confirm_move()
            return

        actions = {
            'snow': self.snow_actions,
            'water': self.water_actions,
            'fire': self.fire_actions
        }

        actions[self.element]()
        self.confirm_move()
        self.debug('select_move complete: confirmed')

    def select_target(self, x: int, y: int) -> None:
        target = next(
            (target for target in self.ninja.targets
            if target.x == x and target.y == y),
            None
        )

        if not target:
            self.debug(f'select_target miss: no target at ({x},{y})')
            return

        self.debug(f'select_target hit: ({x},{y}) type={target.type}')
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

            self.debug(
                'snow heal eval: '
                f'injured={len(injured_allies)} '
                f'move={self.tile_debug(move)} '
                f'target={self.tile_debug(target)}'
            )

            if move:
                self.place_ghost(move)

            if target:
                self.select_target(target.x, target.y)
                return

            # If we can't heal yet, move closer to injured allies so we can next turn
            move = self.best_move_toward_allies(injured_allies)

            self.debug(
                'snow reposition toward allies: '
                f'move={self.tile_debug(move)}'
            )

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

        self.debug(
            'snow attack eval: '
            f'enemies={len(living_enemies)} '
            f'move={self.tile_debug(move)} '
            f'target={self.tile_debug(target)}'
        )

        if move:
            self.place_ghost(move)

        if target:
            self.select_target(target.x, target.y)
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

        self.debug(
            'fire attack eval: '
            f'enemies={len(living_enemies)} '
            f'move={self.tile_debug(move)} '
            f'target={self.tile_debug(target)} '
            f'mode=prefer_farthest_target'
        )

        if move:
            self.place_ghost(move)

        if target:
            self.select_target(target.x, target.y)
            return

        move = self.best_standoff_tile(self.ninja.range)

        self.debug(
            'fire fallback positioning: '
            f'move={self.tile_debug(move)} '
            f'target_standoff={self.ninja.range}'
        )

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

        self.debug(
            'water attack eval: '
            f'enemies={len(living_enemies)} '
            f'move={self.tile_debug(move)} '
            f'target={self.tile_debug(target)} '
            f'mode=prefer_closest_target'
        )

        if move:
            self.place_ghost(move)

        if target:
            self.select_target(target.x, target.y)
            return

        move = self.best_positioning_tile(prefer_far=False)

        if move:
            self.place_ghost(move)

    def place_ghost(self, tile: GameObject) -> None:
        if tile.x == self.ninja.x and tile.y == self.ninja.y:
            self.debug(f'ghost not placed: already on ({tile.x},{tile.y})')
            return

        self.debug(f'ghost placed: ({tile.x},{tile.y}) from ({self.ninja.x},{self.ninja.y})')
        self.ninja.place_ghost(tile.x, tile.y)

    def living_enemies(self) -> list[Enemy]:
        return [enemy for enemy in self.game.enemies if enemy.hp > 0]

    def available_tiles(self) -> list[GameObject]:
        current_tile = self.game.grid[self.ninja.x, self.ninja.y]
        tiles = list(self.ninja.movable_tiles())

        if current_tile:
            tiles.append(current_tile)

        return tiles

    def nearest_enemy_distance(self, tile: GameObject, enemies: Iterable[Enemy]) -> int:
        return min(
            abs(tile.x - enemy.x) + abs(tile.y - enemy.y)
            for enemy in enemies
        )

    def best_enemy_target(
        self,
        targets: list[GameObject],
        from_tile: GameObject,
        prefer_closest: bool
    ) -> GameObject | None:
        enemies = [
            self.game.grid[target.x, target.y]
            for target in targets
        ]
        enemies = [enemy for enemy in enemies if isinstance(enemy, Enemy)]

        if not enemies:
            return None

        def score(enemy: Enemy):
            distance = abs(enemy.x - from_tile.x) + abs(enemy.y - from_tile.y)

            if prefer_closest:
                return (enemy.hp, distance)

            return (enemy.hp, -distance)

        enemy = min(enemies, key=score)
        return self.game.grid.get_tile(enemy.x, enemy.y)

    def best_move_for_attack(
        self,
        enemies: list[Enemy],
        prefer_closest: bool,
        prefer_far_from_enemies: bool
    ) -> tuple[GameObject | None, GameObject | None]:
        best_move = None
        best_targets = []
        best_score = None
        attack_candidates = []

        for tile in self.available_tiles():
            targets = list(self.ninja.attackable_tiles(tile.x, tile.y))

            if not targets:
                continue

            nearest_enemy = self.nearest_enemy_distance(tile, enemies)
            attack_count = len(targets)

            score = (
                attack_count,
                -nearest_enemy if prefer_closest else nearest_enemy
            )
            attack_candidates.append(
                {
                    'tile': (tile.x, tile.y),
                    'attack_count': attack_count,
                    'nearest_enemy': nearest_enemy,
                    'score': score,
                    'targets': [(t.x, t.y) for t in targets]
                }
            )

            if best_score is None or score > best_score:
                best_move = tile
                best_targets = targets
                best_score = score

        if best_move is None:
            if not attack_candidates:
                self.debug('attack eval: no candidate tiles with targets')
                return None, None

            self.debug(
                'attack candidates existed but no best move picked: '
                f'{attack_candidates}'
            )
            return None, None

        target = self.best_enemy_target(
            best_targets, best_move,
            prefer_closest=(not prefer_far_from_enemies)
        )

        self.debug(
            'attack scoring: '
            f'prefer_closest={prefer_closest} '
            f'prefer_far_from_enemies={prefer_far_from_enemies} '
            f'candidates={attack_candidates} '
            f'chosen_move={self.tile_debug(best_move)} '
            f'chosen_target={self.tile_debug(target)} '
            f'chosen_score={best_score}'
        )
        return best_move, target

    def best_standoff_tile(self, target_distance: int) -> GameObject | None:
        enemies = self.living_enemies()

        if not enemies:
            return None

        tiles = self.available_tiles()

        if not tiles:
            return None

        current_tile = self.game.grid[self.ninja.x, self.ninja.y]

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

        self.debug(
            'standoff eval: '
            f'target_distance={target_distance} '
            f'chosen_tile={self.tile_debug(best_tile)} '
            f'chosen_distance={self.nearest_enemy_distance(best_tile, enemies)}'
        )

        return best_tile

    def best_move_for_heal(self, allies: list[Ninja]) -> tuple[GameObject | None, GameObject | None]:
        best_move = None
        best_target = None
        best_score = None
        heal_candidates = []

        for tile in self.available_tiles():
            heal_tiles = list(self.ninja.healable_tiles(tile.x, tile.y))

            if not heal_tiles:
                continue

            for heal_tile in heal_tiles:
                ally = self.game.grid[heal_tile.x, heal_tile.y]

                if not isinstance(ally, Ninja):
                    continue

                missing_hp = ally.max_hp - ally.hp
                score = (1, missing_hp)

                if ally.hp <= 0:
                    # Prioritize revives above regular heals
                    score = (2, 0)

                heal_candidates.append(
                    {
                        'from': (tile.x, tile.y),
                        'target': (heal_tile.x, heal_tile.y),
                        'ally_hp': ally.hp,
                        'ally_max_hp': ally.max_hp,
                        'score': score
                    }
                )

                if best_score is None or score > best_score:
                    best_move = tile
                    best_target = heal_tile
                    best_score = score

        self.debug(
            'heal scoring: '
            f'allies={len(allies)} '
            f'candidates={heal_candidates} '
            f'chosen_move={self.tile_debug(best_move)} '
            f'chosen_target={self.tile_debug(best_target)} '
            f'chosen_score={best_score}'
        )
        return best_move, best_target

    def best_positioning_tile(self, prefer_far: bool) -> GameObject | None:
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

        self.debug(
            'positioning eval: '
            f'prefer_far={prefer_far} '
            f'best_tile={self.tile_debug(best_tile)} '
            f'distance={self.nearest_enemy_distance(best_tile, enemies)}'
        )
        return best_tile

    def best_move_toward_allies(self, allies: list[Ninja]) -> GameObject | None:
        """Move Snow closer to injured allies to improve heal reach next turn."""
        if not allies:
            return None

        tiles = self.available_tiles()

        if not tiles:
            return None

        current_tile = self.game.grid[self.ninja.x, self.ninja.y]

        # Prefer tiles that reduce average distance to allies
        # On ties, prefer moving over staying
        best_tile = min(
            tiles,
            key=lambda tile: (
                sum(abs(tile.x - ally.x) + abs(tile.y - ally.y) for ally in allies) / len(allies),
                0 if (current_tile and tile != current_tile) else 1
            )
        )

        avg_distance = sum(
            abs(best_tile.x - ally.x) + abs(best_tile.y - ally.y)
            for ally in allies
        ) / len(allies)

        self.debug(
            'ally proximity eval: '
            f'allies={len(allies)} '
            f'chosen_tile={self.tile_debug(best_tile)} '
            f'avg_distance={avg_distance:.1f}'
        )

        return best_tile

    def is_ninja_getting_revived(self, ninja: Ninja) -> bool:
        for ninja in self.game.ninjas:
            if ninja.selected_object == ninja:
                return True

        return False

    def can_heal_ninja(self, target: Ninja) -> bool:
        tiles = self.game.grid.surrounding_tiles(
            target.x,
            target.y
        )

        for tile in tiles:
            can_move = self.game.grid.can_move_to_tile(
                self.ninja,
                tile.x,
                tile.y
            )

            if not can_move:
                continue

            self.ninja.place_ghost(tile.x, tile.y)
            return True

        current_tile = self.game.grid[self.ninja.x, self.ninja.y]

        if current_tile in tiles:
            return True

        return False

    def unlock_stamp(self, id=..., session=...) -> None:
        # Bots don't have an account for stamps
        pass
