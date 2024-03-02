
from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Tuple, List
from twisted.internet import reactor

if TYPE_CHECKING:
    from app.objects.ninjas import Ninja
    from app.engine.tusk import TuskGame
    from app.engine.game import Game
    from app.engine import Penguin

from app.data import MirrorMode
from app.objects import GameObject
from app.objects.effects import (
    ScrapImpactSurroundings,
    ScrapProjectileImpact,
    TankSwipeHorizontal,
    TankSwipeVertical,
    DamageNumbers,
    TuskIcicleRow,
    SlyProjectile,
    TuskPushRock,
    ScrapImpact,
    TuskIcicle,
    AttackTile,
    Explosion,
    Effect,
    Flame
)

import itertools
import random
import time

class Enemy(GameObject):
    name: str = 'Enemy'
    max_hp: int = 0
    range: int = 0
    attack: int = 0
    move: int = 0
    tile_range: int = 0
    move_duration: int = 600

    def __init__(
        self,
        game: "Game",
        x: int = -1,
        y: int = -1
    ) -> None:
        super().__init__(
            game,
            self.__class__.name,
            x, y,
            grid=True,
            x_offset=0.5,
            y_offset=1
        )
        self.hp = self.__class__.max_hp
        self.move = self.__class__.move
        self.range = self.__class__.range
        self.attack = self.__class__.attack
        self.max_hp = self.__class__.max_hp
        self.tile_range = self.__class__.tile_range
        self.move_duration = self.__class__.move_duration

        self.health_bar = GameObject(
            self.game,
            'reghealthbar_animation',
            x=self.x,
            y=self.y,
            x_offset=0.5,
            y_offset=1.005
        )

        self.flame: Flame | None = None
        self.stunned = False

    def remove_object(self) -> None:
        self.health_bar.remove_object()
        super().remove_object()

        if self.flame:
            self.flame.remove_object()

    def spawn(self) -> None:
        self.spawn_animation()
        self.idle_animation()

    def move_object(self, x: int, y: int) -> None:
        if self.flame:
            self.flame.move_object(x, y, self.move_duration)

        self.health_bar.move_object(x, y, self.move_duration)
        super().move_object(x, y, self.move_duration)

    def move_enemy(self, x: int, y: int) -> None:
        if self.hp <= 0:
            return

        if self.x == x and self.y == y:
            return

        if self.x < x:
            self.mirror_mode = MirrorMode.X

        self.move_animation()
        self.move_object(x, y)
        self.move_sound()

    def place_healthbar(self) -> None:
        self.health_bar.x = self.x
        self.health_bar.y = self.y
        self.health_bar.place_object()
        self.health_bar.place_sprite(self.health_bar.name)
        self.reset_healthbar()

    def animate_healthbar(self, start_hp: int, end_hp: int, duration: int = 500) -> None:
        backwards = False

        if end_hp > start_hp:
            # Health increased, playing backwards
            backwards = True

            # Swap start and end hp
            start_hp, end_hp = end_hp, start_hp

        start_frame = 60 - int((start_hp / self.max_hp) * 60)
        end_frame = 60 - int((end_hp / self.max_hp) * 60)

        self.health_bar.animate_sprite(
            start_frame-1,
            end_frame-1,
            backwards=backwards,
            duration=duration
        )

    def reset_healthbar(self) -> None:
        self.health_bar.animate_sprite()

    def set_health(self, hp: int, wait=True) -> None:
        hp = max(0, min(hp, self.max_hp))
        self.animate_healthbar(self.hp, hp, duration=500)

        AttackTile(
            self.game,
            self.x,
            self.y
        ).play(auto_remove=True)

        DamageNumbers(
            self.game,
            self.x,
            self.y
        ).play(self.hp - hp)

        self.hp = hp

        if self.hp <= 0:
            self.ko_animation()

            if not wait:
                reactor.callLater(2.5, self.remove_object)
                return

            self.game.wait_for_animations()
            self.remove_object()
            return

        self.hit_animation()

    def attack_target(self, target: "Ninja") -> None:
        if target.hp <= 0:
            return

        # This seems to fix the mirror mode?
        time.sleep(0.25)

        self.attack_animation()
        target.set_health(target.hp - self.attack)

    def flame_damage(self) -> None:
        if self.hp <= 0:
            return

        self.set_health(self.hp - 3)

    def update_flame(self) -> None:
        if not self.flame:
            return

        if self.flame.rounds_left <= 0:
            # Stun enemy one more time before removing flame
            self.flame_damage()

            self.flame.remove_object()
            self.flame = None

            # Reset animation
            reactor.callLater(0.8, self.idle_animation, True)
            return

        self.flame.rounds_left -= 1
        self.flame_damage()

    def movable_tiles(self) -> Iterator[GameObject]:
        """Get all tiles that the enemy can move to from its current position"""
        for tile in self.game.grid.tiles:
            if not self.game.grid.can_move(tile.x, tile.y):
                continue

            distance = self.game.grid.distance_with_obstacles(
                (self.x, self.y),
                (tile.x, tile.y)
            )

            if distance <= self.move:
                yield tile

    def attackable_tiles(self, target_x: int, target_y: int, range: int | None = None) -> Iterator[GameObject]:
        """Get all tiles that the enemy can attack from its current position"""
        for tile in self.game.grid.tiles:
            target_object = self.game.grid[tile.x, tile.y]

            if not target_object:
                continue

            if not target_object.name in ('Water', 'Fire', 'Snow'):
                continue

            if target_object.hp <= 0:
                continue

            distance = self.game.grid.distance_with_obstacles(
                (target_x, target_y),
                (tile.x, tile.y)
            )

            if distance <= (range or self.range):
                yield tile

    def next_target(self) -> Tuple[GameObject | None, GameObject | None]:
        """Find and return the next move and attack"""
        available_moves = list(self.movable_tiles()) + [self.game.grid[self.x, self.y]]

        if not available_moves:
            # TODO: Handle this case properly
            return None, None

        # Get move with most available targets
        moves = {
            move: list(self.attackable_tiles(move.x, move.y))
            for move in available_moves
        }

        if not any(moves.values()):
            # No targets in range, move to the closest possible tile
            return self.closest_move(), None

        for move, targets in list(moves.items()):
            # Check if there are any targets
            if not targets:
                moves.pop(move)
                continue

            # Sort targets by most damage
            moves[move].sort(
                key=lambda target: self.simulate_damage(
                    move.x,
                    move.y,
                    target
                ),
                reverse=True
            )

        # Sort moves by most damage
        sorted_moves = sorted(
            moves.items(),
            key=lambda m: self.simulate_damage(
                m[0].x,
                m[0].y,
                m[1][0]
            ),
            reverse=True
        )

        highest_damage = self.simulate_damage(
            sorted_moves[0][0].x,
            sorted_moves[0][0].y,
            sorted_moves[0][1][0]
        )

        # If multiple moves have the same damage, pick a random one
        next_move, targets = random.choice([
            (move, targets) for move, targets in sorted_moves
            if self.simulate_damage(move.x, move.y, targets[0]) == highest_damage
        ])

        return next_move, targets[0]

    def closest_move(self) -> GameObject | None:
        """Get the closest tile to a ninja, that the enemy can move to"""

        # TODO: This method can sometimes lead to the enemy being stuck
        #       if the target is behind an obstacle. We should probably
        #       implement a pathfinding algorithm to fix this.

        if not (tiles := list(self.movable_tiles())):
            # Enemy can't move
            return

        # Get all ninja tiles, and sort them by distance to enemy
        tiles = [
            min(
                tiles,
                key=lambda tile: abs(tile.x - ninja.x) + abs(tile.y - ninja.y)
            )
            for ninja in self.game.ninjas
            if ninja.hp > 0
        ]

        if not tiles:
            # No available tiles
            return

        # Return tile that is closest to enemy
        return min(
            tiles,
            key=lambda tile: abs(tile.x - self.x) + abs(tile.y - self.y)
        )

    def simulate_damage(self, x_position: int, y_position: int, target: GameObject) -> int:
        """Simulate the damage that the enemy would do to a target"""
        return self.attack

    """Animations"""

    def spawn_animation(self) -> None:
        self.animate_object(
            f'snowman_spawn_anim',
            play_style='play_once',
            reset=True
        )
        self.spawn_sound()

    def idle_animation(self, reset=False) -> None:
        ...

    def move_animation(self) -> None:
        ...

    def attack_animation(self) -> None:
        ...

    def ko_animation(self) -> None:
        ...

    def hit_animation(self) -> None:
        ...

    def daze_animation(self, reset=True) -> None:
        ...

    """Sounds"""

    def spawn_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_snowmenappear')

    def ko_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_snowmandeathexplode')

    def move_sound(self) -> None:
        ...

    def attack_sound(self) -> None:
        ...

    def hit_sound(self) -> None:
        ...

    def impact_sound(self) -> None:
        ...

class Sly(Enemy):
    name: str = 'Sly'
    max_hp: int = 30
    range: int = 3
    attack: int = 3
    attack_per_tile: int = 1
    move: int = 3
    move_duration: int = 1200

    def simulate_damage(self, x_position: int, y_position: int, target: GameObject) -> int:
        """Simulate the damage that the enemy would do to a target"""
        distance = abs(x_position - target.x) + abs(y_position - target.y)

        # NOTE: Sly hits harder from a distance. According to the
        #       Wiki, it does an additional 1 damage per tile
        return self.attack + round(self.attack_per_tile * (distance - 2))

    def attack_target(self, target: "Ninja") -> None:
        if target.hp <= 0:
            return

        # This seems to fix the mirror mode?
        time.sleep(0.25)

        self.attack_animation(target.x, target.y)
        target.set_health(
            target.hp - self.simulate_damage(self.x, self.y, target)
        )

    def idle_animation(self, reset=False) -> None:
        self.animate_object(
            f'sly_idle_anim',
            play_style='loop',
            register=False,
            reset=reset
        )

    def move_animation(self) -> None:
        self.animate_object(
            'sly_move_anim',
            play_style='loop',
            reset=True
        )
        self.idle_animation()

    def attack_animation(self, x: int, y: int) -> None:
        if self.x < x:
            self.mirror_mode = MirrorMode.X

        time.sleep(0.25)
        self.animate_object(
            'sly_attack_anim',
            play_style='play_once',
            callback=self.reset_sprite_settings,
            reset=True
        )
        self.idle_animation()
        self.attack_sound()

        time.sleep(1.45)
        projectile = SlyProjectile(self.game, self.x, self.y)
        projectile.play(x, y)

        time.sleep(0.5)
        self.impact_sound()
        projectile.remove_object()

        Explosion(
            self.game,
            x,
            y
        ).play()

    def ko_animation(self) -> None:
        self.animate_object(
            'sly_ko_anim',
            play_style='play_once',
            reset=True
        )
        self.ko_sound()

    def hit_animation(self) -> None:
        self.animate_object(
            'sly_hit_anim',
            play_style='play_once',
            reset=True
        )
        self.hit_sound()

        if self.stunned:
            self.daze_animation(False)
            return

        self.idle_animation()

    def daze_animation(self, reset=True) -> None:
        self.animate_object(
            'sly_daze_anim',
            play_style='loop',
            reset=reset
        )

    def move_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_footstepsly_loop')

    def hit_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_snowmanslyhit')

    def attack_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attacksly')

    def impact_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_impactsly')

class Scrap(Enemy):
    name: str = 'Scrap'
    max_hp: int = 45
    range: int = 2
    attack: int = 8
    move: int = 2
    move_duration: int = 1200

    def simulate_damage(self, x_position: int, y_position: int, target: GameObject) -> int:
        """Simulate the damage that the enemy would do to a target"""
        surrounding_targets = list(self.attackable_tiles(target.x, target.y, range=1))
        surrounding_targets.remove(target)

        return self.attack + (self.attack / 2) * len(surrounding_targets)

    def attack_target(self, target: "Ninja") -> None:
        if target.hp <= 0:
            return

        # This seems to fix the mirror mode?
        time.sleep(0.25)

        self.attack_animation(target.x, target.y)
        target.set_health(target.hp - self.attack)

        ScrapProjectileImpact(
            self.game,
            target.x,
            target.y
        ).play()

        surrounding_targets = [
            object for object in self.game.grid.surrounding_objects(target.x, target.y)
            if object.name in ('Water', 'Fire', 'Snow') and object.hp > 0
        ]

        if surrounding_targets:
            self.impact_sound()

        for surrounding_target in surrounding_targets:
            object = self.game.grid[surrounding_target.x, surrounding_target.y]
            object.set_health(object.hp - self.attack / 2)

            Explosion(
                self.game,
                surrounding_target.x,
                surrounding_target.y
            ).play()

        ScrapImpactSurroundings(
            self.game,
            target.x,
            target.y
        ).play()

    def idle_animation(self, reset=False) -> None:
        self.animate_object(
            'scrap_idle_anim',
            play_style='loop',
            register=False,
            reset=reset
        )

    def move_animation(self) -> None:
        self.animate_object(
            'scrap_move_anim',
            play_style='loop',
            reset=True
        )
        self.idle_animation()
        self.move_sound()

    def attack_animation(self, x: int, y: int) -> None:
        if self.x < x:
            self.mirror_mode = MirrorMode.X

        self.animate_object(
            f'scrap_attack_anim',
            play_style='play_once',
            callback=self.reset_sprite_settings,
            reset=True
        )
        self.idle_animation()

        time.sleep(0.7)
        self.attack_sound()

        distance = abs(self.x - x) + abs(self.y - y)
        impact_time = 0.9 + (distance * 0.1)

        time.sleep(impact_time)
        self.impact_sound()

        ScrapImpact(self.game, x, y).play()

    def ko_animation(self) -> None:
        self.animate_object(
            'scrap_ko_anim',
            play_style='play_once',
            reset=True
        )
        self.ko_sound()

    def hit_animation(self) -> None:
        self.animate_object(
            'scrap_hit_anim',
            play_style='play_once',
            reset=True
        )
        self.hit_sound()

        if self.stunned:
            self.daze_animation(False)
            return

        self.idle_animation()

    def daze_animation(self, reset=True) -> None:
        self.animate_object(
            'scrap_dazed_anim',
            play_style='loop',
            reset=reset
        )

    def move_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_footstepscrap_loop')

    def hit_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_snowmanscraphit')

    def attack_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attackscrap')

    def impact_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_impactscrap')

class Tank(Enemy):
    name: str = 'Tank'
    max_hp: int = 60
    range: int = 1
    attack: int = 10
    move: int = 1
    move_duration: int = 1100

    def simulate_damage(self, x_position: int, y_position: int, target: GameObject) -> int:
        """Simulate the damage that the enemy would do to a target"""
        # Horizontal swipe
        if x_position == target.x:
            total_damage = self.attack

            left = self.game.grid[x_position-1, y_position]
            right = self.game.grid[x_position+1, y_position]

            if left is not None and left.name in ('Water', 'Fire', 'Snow'):
                total_damage += self.attack / 2

            if right is not None and right.name in ('Water', 'Fire', 'Snow'):
                total_damage += self.attack / 2

            return total_damage

        # Vertical swipe
        elif y_position == target.y:
            total_damage = self.attack

            above = self.game.grid[x_position, y_position-1]
            below = self.game.grid[x_position, y_position+1]

            if above is not None and above.name in ('Water', 'Fire', 'Snow'):
                total_damage += self.attack / 2

            if below is not None and below.name in ('Water', 'Fire', 'Snow'):
                total_damage += self.attack / 2

            return total_damage

        # This should never happen, unless range is greater than 1
        return self.attack

    def attack_target(self, target: "Ninja") -> None:
        if target.hp <= 0:
            return

        # This seems to fix the mirror mode?
        time.sleep(0.25)

        self.attack_animation(target.x, target.y)
        target.set_health(target.hp - self.attack)

        effects: List[Effect] = []

        if self.x == target.x:
            left = self.game.grid[target.x-1, target.y]
            right = self.game.grid[target.x+1, target.y]

            if left is not None and left.name in ('Water', 'Fire', 'Snow'):
                left.set_health(left.hp - self.attack / 2)

            if right is not None and right.name in ('Water', 'Fire', 'Snow'):
                right.set_health(right.hp - self.attack / 2)

            effects = [
                TankSwipeHorizontal(self.game, target.x, target.y+1),
                AttackTile(self.game, target.x-1, target.y),
                AttackTile(self.game, target.x+1, target.y),
                AttackTile(self.game, target.x, target.y)
            ]

        elif self.y == target.y:
            above = self.game.grid[target.x, target.y-1]
            below = self.game.grid[target.x, target.y+1]

            if above is not None and above.name in ('Water', 'Fire', 'Snow'):
                above.set_health(above.hp - self.attack / 2)

            if below is not None and below.name in ('Water', 'Fire', 'Snow'):
                below.set_health(below.hp - self.attack / 2)

            effects = [
                TankSwipeVertical(self.game, target.x, target.y),
                AttackTile(self.game, target.x, target.y-1),
                AttackTile(self.game, target.x, target.y+1),
                AttackTile(self.game, target.x, target.y)
            ]

        for attack_tile in effects:
            attack_tile.play()

        time.sleep(0.25)

        for attack_tile in effects:
            attack_tile.remove_object()

    def idle_animation(self, reset=False) -> None:
        self.animate_object(
            'tank_idle_anim',
            play_style='loop',
            register=False,
            reset=reset
        )

    def move_animation(self) -> None:
        self.animate_object(
            f'tank_move_anim',
            play_style='loop',
            reset=True
        )
        self.idle_animation()
        self.move_sound()

    def attack_animation(self, x: int, y: int) -> None:
        if self.x < x:
            self.mirror_mode = MirrorMode.X

        self.attack_sound()
        self.animate_object(
            f'tank_attack_anim',
            play_style='play_once',
            callback=self.reset_sprite_settings,
            reset=True
        )
        self.idle_animation()
        time.sleep(0.15)

    def ko_animation(self) -> None:
        self.animate_object(
            'tank_ko_anim',
            play_style='play_once',
            reset=True
        )
        self.ko_sound()

    def hit_animation(self) -> None:
        self.animate_object(
            'tank_hit_anim',
            play_style='play_once',
            reset=True
        )
        self.hit_sound()

        if self.stunned:
            self.daze_animation(False)
            return

        self.idle_animation()

    def daze_animation(self, reset=True) -> None:
        self.animate_object(
            f'tank_daze_anim',
            play_style='loop',
            reset=reset
        )

    def move_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_footsteptank')

    def hit_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_snowmantankhit')

    def attack_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attacktank')

class Tusk(Enemy):
    name: str = 'Tusk'
    max_hp: int = 800
    attack: int = 10
    range: int = 9
    move: int = 0
    tile_range: int = 1

    def __init__(
        self,
        game: "TuskGame",
        x: int = -1,
        y: int = -1
    ) -> None:
        super().__init__(game, x, y)
        self.health_bar = GameObject(
            self.game,
            'tusk_healthbar_animation',
            x=self.x,
            y=self.y,
            x_offset=0.5,
            y_offset=1.005
        )

        # First attack will either be 'push' or 'icicle_random'
        self.next_attack = random.choice([
            'push',
            'icicle_random'
        ])

        # Icicle rows used for the 'icicle_paired' attack
        self.icicle_pairs = itertools.cycle([
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4)
        ])

        # Block tiles around tusk to match sprite's size

        # Next to tusk
        self.game.grid.block_tile(self.x - 1, self.y)
        # Below tusk
        self.game.grid.block_tile(self.x - 1, self.y + 1)
        self.game.grid.block_tile(self.x, self.y + 1)
        # Above tusk
        self.game.grid.block_tile(self.x - 1, self.y - 1)
        self.game.grid.block_tile(self.x, self.y - 1)

    def attack_target(self, target: "Ninja") -> None:
        if target.hp <= 0:
            return

        attacks = {
            'push': self.push_attack,
            'icicle_random': self.icicle_attack_random,
            'icicle_paired': self.icicle_attack_paired
        }

        attacks[self.next_attack]()
        self.determine_next_attack(target)

    def determine_next_attack(self, closest_target: "Ninja") -> None:
        if self.next_attack in ('icicle_random', 'push'):
            self.next_attack = 'icicle_paired'
            return

        self.next_attack = 'icicle_random'

        # The closer the ninjas are to tusk, the higher the chance for a "push" attack
        distance = (
            abs(self.x - closest_target.x) + abs(self.y - closest_target.y)
        )

        push_attack_chance = abs(
            1 - ((distance - 1) / 7)
        )

        if random.random() <= push_attack_chance:
            self.next_attack = 'push'

    def push_attack(self) -> None:
        self.push_attack_animation()

        push_duration = 2.25
        attack_delay = 1.85

        ninjas = self.game.ninjas
        ninjas.sort(key=lambda ninja: ninja.x)
        ninja_positions = []

        for ninja in ninjas:
            # Determine the end position for the push
            result_x = 0

            while (
                (result_x, ninja.y) in ninja_positions or
                not self.game.grid.can_move(result_x, ninja.y)
            ):
                result_x += 1

            if result_x < ninja.x:
                # Move ninja to the left
                reactor.callLater(
                    attack_delay, ninja.move_object,
                    result_x, ninja.y,
                    push_duration * 1000
                )

            if ninja.hp > 0:
                # Apply damage
                reactor.callLater(
                    attack_delay + (push_duration / 1.5),
                    ninja.set_health,
                    ninja.hp - self.attack, False
                )

            if result_x > ninja.x:
                result_x = ninja.x

            ninja_positions.append((result_x, ninja.y))

        time.sleep(attack_delay)
        x_range = list(self.game.grid.x_range)
        x_range.reverse()

        # NOTE: This should be a pretty accurate representation of the push attack
        #       However, the actual algorithm for this attack is unknown

        positions = [
            (1, 0),
            (1, 2),
            (0, 4),
            (0, 1),
            (1, 3)
        ]

        for x in x_range:
            first_positions = positions[:3]
            last_positions = positions[2:]

            for base_x, base_y in first_positions:
                if x - base_x < 0:
                    continue

                TuskPushRock(
                    self.game,
                    x - base_x,
                    base_y
                ).play()

            time.sleep((push_duration / len(x_range)) / 2)

            for base_x, base_y in last_positions:
                if x - base_x < 0:
                    continue

                TuskPushRock(
                    self.game,
                    x - base_x,
                    base_y
                ).play()

            time.sleep((push_duration / len(x_range)) / 2)

        self.game.wait_for_animations()

    def icicle_attack_random(self) -> None:
        self.icicle_attack_animation()
        time.sleep(1.1)

        # NOTE: The actual algorithm for this attack is unknown
        #       I am just going to improvise for now

        # Select random tiles to drop icicles on
        random_positions = random.sample(
            [
                (tile.x, tile.y)
                for tile in self.game.grid.tiles
            ],
            random.randint(1, 6 - len(self.game.connected_clients))
        )

        # Lower the possibility of hitting ninjas
        ninja_hit_chance = (len(self.game.connected_clients) / 10) + 0.2
        ninja_positions = []

        if random.random() <= ninja_hit_chance:
            # Select random ninjas to drop icicles on
            ninja_positions = random.sample(
                [
                    (ninja.x, ninja.y)
                    for ninja in self.game.ninjas
                    if not ninja.client.disconnected
                ],
                random.randint(1, len(self.game.connected_clients))
            )

        positions = set(random_positions + ninja_positions)

        for x, y in positions:
            TuskIcicle(self.game, x, y).play()

        time.sleep(1.5)
        self.game.wait_for_animations()

    def icicle_attack_paired(self) -> None:
        self.icicle_attack_animation()
        time.sleep(1.1)
        effect = TuskIcicleRow(
            self.game,
            next(self.icicle_pairs)
        )
        effect.play()

        time.sleep(1)
        self.game.wait_for_animations()

    def set_health(self, hp: int, wait=True) -> None:
        hp = max(0, min(hp, self.max_hp))
        self.animate_healthbar(self.hp, hp, duration=500)

        # Update damage percentage for payout
        self.game.damage = round(100 - ((hp / self.max_hp) * 100))

        AttackTile(
            self.game,
            self.x,
            self.y
        ).play(auto_remove=True)

        DamageNumbers(
            self.game,
            self.x,
            self.y
        ).play(self.hp - hp)

        self.hp = hp

        if self.hp <= 0:
            self.ko_animation()
            self.game.wait_for_animations()
            self.remove_object()
            return

        self.hit_animation()

    def animate_healthbar(self, start_hp: int, end_hp: int, duration: int = 500) -> None:
        backwards = False

        if end_hp > start_hp:
            # Health increased, playing backwards
            backwards = True

            # Swap start and end hp
            start_hp, end_hp = end_hp, start_hp

        start_frame = 240 - int((start_hp / self.max_hp) * 240)
        end_frame = 240 - int((end_hp / self.max_hp) * 240)

        self.health_bar.animate_sprite(
            start_frame-1,
            end_frame-1,
            backwards=backwards,
            duration=duration
        )

    def idle_animation(self, reset=False) -> None:
        self.animate_object(
            'tusk_idle_anim',
            play_style='loop',
            register=False,
            reset=reset
        )

    def push_attack_animation(self) -> None:
        self.animate_object(
            'tusk_pushattack_anim',
            play_style='play_once',
            reset=True
        )
        self.push_attack_sound()
        self.idle_animation()

    def icicle_attack_animation(self) -> None:
        self.icicle_attack_sound_start()
        self.animate_object(
            'tusk_iciclesummon1_anim',
            play_style='play_once',
            reset=True
        )
        self.animate_sprite(0, 25, duration=1300)
        self.game.wait_for_animations()
        self.icicle_attack_sound_end()
        self.animate_object(
            'tusk_iciclesummon2_anim',
            play_style='play_once'
        )
        self.idle_animation()

    def ko_animation(self) -> None:
        self.animate_object(
            'tusk_lose_anim',
            play_style='play_once',
            reset=True
        )

    def win_animation(self) -> None:
        self.animate_object(
            'tusk_win_anim',
            play_style='play_once',
            reset=True
        )
        self.laugh_sound()

    def hit_animation(self) -> None:
        self.animate_object(
            'tusk_hit_anim',
            play_style='play_once',
            reset=True
        )
        self.hit_sound()

        if self.stunned:
            self.daze_animation(False)
            return

        self.idle_animation()

    def daze_animation(self, reset=True) -> None:
        self.animate_object(
            'tusk_stun_anim',
            play_style='loop',
            reset=reset
        )

    def hit_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_hittusk')

    def laugh_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_tusklaugh')

    def push_attack_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attacktuskearthquake')

    def icicle_attack_sound_start(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attacktuskicicle01')

    def icicle_attack_sound_end(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attacktuskicicle02')
