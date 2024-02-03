
from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Tuple, List

if TYPE_CHECKING:
    from app.objects.ninjas import Ninja
    from app.engine.game import Game

from app.data import MirrorMode

from app.objects.effects import (
    TankSwipeHorizontal,
    TankSwipeVertical,
    AttackTile,
    Effect
)

from app.objects import (
    SoundCollection,
    AssetCollection,
    GameObject,
    Sound,
    Asset
)

import random
import time

class Enemy(GameObject):
    name: str = 'Enemy'
    max_hp: int = 0
    range: int = 0
    attack: int = 0
    move: int = 0
    move_duration: int = 600

    assets = AssetCollection()
    sounds = SoundCollection()

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
        self.assets = self.__class__.assets
        self.sounds = self.__class__.sounds
        self.attack = self.__class__.attack
        self.range = self.__class__.range
        self.max_hp = self.__class__.max_hp
        self.hp = self.max_hp
        self.initialize_objects()

    def initialize_objects(self) -> None:
        self.health_bar = GameObject.from_asset(
            'reghealthbar_animation',
            self.game,
            x=self.x,
            y=self.y,
            x_offset=0.5,
            y_offset=1
        )

    def remove_object(self) -> None:
        self.health_bar.remove_object()
        super().remove_object()

    def spawn(self) -> None:
        self.spawn_animation()
        self.idle_animation()

    def move_object(self, x: int, y: int) -> None:
        self.health_bar.move_object(x, y, self.move_duration)
        super().move_object(x, y, self.move_duration)

    def move_enemy(self, x: int, y: int) -> None:
        if self.hp <= 0:
            return

        if self.x == x and self.y == y:
            return

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

    def set_health(self, hp: int) -> None:
        hp = max(0, min(hp, self.max_hp))
        self.animate_healthbar(self.hp, hp, duration=500)
        self.hp = hp

        if self.hp <= 0:
            self.ko_animation()
            self.game.wait_for_animations()
            self.remove_object()
        else:
            self.hit_animation()

    def attack_target(self, target: "Ninja") -> None:
        if target.hp <= 0:
            return

        # This seems to fix the mirror mode?
        time.sleep(0.25)

        self.attack_animation()
        target.set_health(target.hp - self.attack)

    def movable_tiles(self) -> Iterator[GameObject]:
        for tile in self.game.grid.tiles:
            if not self.game.grid.can_move(tile.x, tile.y):
                continue

            distance = abs(tile.x - self.x) + abs(tile.y - self.y)

            if distance <= self.move:
                yield tile

    def attackable_tiles(self, target_x: int, target_y: int, range: int | None = None) -> Iterator[GameObject]:
        for tile in self.game.grid.tiles:
            target_object = self.game.grid[tile.x, tile.y]

            if not target_object:
                continue

            if isinstance(target_object, Enemy):
                continue

            if target_object.hp <= 0:
                continue

            distance = abs(tile.x - target_x) + abs(tile.y - target_y)

            if distance <= (range or self.range):
                yield tile

    def next_target(self) -> Tuple[GameObject, GameObject | None]:
        available_moves = list(self.movable_tiles()) + [self.game.grid[self.x, self.y]]

        # Get move with most available targets
        moves = {
            move: list(self.attackable_tiles(move.x, move.y))
            for move in available_moves
        }

        if not any(moves.values()):
            # No targets in range
            return self.closest_target(), None

        for move, targets in list(moves.items()):
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
        next_move, targets = sorted(
            moves.items(),
            key=lambda m: self.simulate_damage(
                m[0].x,
                m[0].y,
                m[1][0]
            ),
            reverse=True
        )[0]

        return next_move, targets[0]

    def closest_target(self) -> GameObject | None:
        # Get all enemy tiles
        tiles = [
            min(
                self.movable_tiles(),
                key=lambda tile: abs(tile.x - ninja.x) + abs(tile.y - ninja.y)
            )
            for ninja in self.game.ninjas
            if ninja.hp > 0
        ]

        if not tiles:
            return

        # Return tile that is closest to enemy
        return min(
            tiles,
            key=lambda tile: abs(tile.x - self.x) + abs(tile.y - self.y)
        )

    def simulate_damage(self, x_position: int, y_position: int, target: GameObject) -> int:
        ...

    def spawn_animation(self) -> None:
        self.animate_object(
            f'snowman_spawn_anim',
            play_style='play_once',
            reset=True
        )
        self.spawn_sound()

    def idle_animation(self) -> None:
        ...

    def move_animation(self) -> None:
        ...

    def attack_animation(self) -> None:
        ...

    def ko_animation(self) -> None:
        ...

    def hit_animation(self) -> None:
        ...

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
    attack: int = 4
    move: int = 3
    move_duration: int = 1200

    assets = AssetCollection({
        Asset.from_name('sly_idle_anim'),
        Asset.from_name('sly_attack_anim'),
        Asset.from_name('sly_move_anim'),
        Asset.from_name('sly_hit_anim'),
        Asset.from_name('sly_ko_anim'),
        Asset.from_name('sly_projectile_anim'),
        Asset.from_name('sly_daze_anim'),
        Asset.from_name('snowman_spawn_anim')
    })
    sounds = SoundCollection({
        Sound.from_name('sfx_mg_2013_cjsnow_footstepsly_loop'),
        Sound.from_name('sfx_mg_2013_cjsnow_attacksly'),
        Sound.from_name('sfx_mg_2013_cjsnow_impactsly'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmanslyhit'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmenappear'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmandeathexplode')
    })

    def simulate_damage(self, x_position: int, y_position: int, target: GameObject) -> int:
        distance = abs(x_position - target.x) + abs(y_position - target.y)

        # NOTE: Sly hits harder from a distance. I don't know how much
        #       damage he does, so I'm just making up a formula.
        return round(self.attack * max(1, distance * 0.45))

    def attack_target(self, target: "Ninja") -> None:
        if target.hp <= 0:
            return

        # This seems to fix the mirror mode?
        time.sleep(0.25)

        self.attack_animation(target.x, target.y)
        target.set_health(
            target.hp - self.simulate_damage(self.x, self.y, target)
        )

    def idle_animation(self) -> None:
        self.animate_object(
            f'sly_idle_anim',
            play_style='loop',
            register=False
        )

    def move_animation(self) -> None:
        self.animate_object(
            f'sly_move_anim',
            play_style='loop',
            reset=True
        )
        self.idle_animation()

    def attack_animation(self, x: int, y: int) -> None:
        if self.x < x:
            self.mirror_mode = MirrorMode.X

        time.sleep(0.25)
        self.animate_object(
            f'sly_attack_anim',
            play_style='play_once',
            callback=self.reset_sprite_settings,
            reset=True
        )
        self.attack_sound()
        self.idle_animation()

        time.sleep(1.85)
        self.impact_sound()

        # TODO: Snowball particle

    def ko_animation(self) -> None:
        self.animate_object(
            f'sly_ko_anim',
            play_style='play_once',
            reset=True
        )
        self.ko_sound()

    def hit_animation(self) -> None:
        self.animate_object(
            f'sly_hit_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()
        self.hit_sound()

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
    attack: int = 5
    move: int = 2
    move_duration: int = 1200

    assets = AssetCollection({
       Asset.from_name('scrap_idle_anim'),
       Asset.from_name('scrap_attack_anim'),
       Asset.from_name('scrap_attackeffect_anim'),
       Asset.from_name('scrap_attacklittleeffect_anim'),
       Asset.from_name('scrap_projectileeast_anim'),
       Asset.from_name('scrap_projectilenorth_anim'),
       Asset.from_name('scrap_projectilenortheast_anim'),
       Asset.from_name('scrap_hit_anim'),
       Asset.from_name('scrap_move_anim'),
       Asset.from_name('scrap_ko_anim'),
       Asset.from_name('scrap_dazed_anim'),
       Asset.from_name('snowman_spawn_anim')
    })
    sounds = SoundCollection({
        Sound.from_name('sfx_mg_2013_cjsnow_snowmanscraphit'),
        Sound.from_name('sfx_mg_2013_cjsnow_impactscrap'),
        Sound.from_name('sfx_mg_2013_cjsnow_footstepscrap_loop'),
        Sound.from_name('sfx_mg_2013_cjsnow_attackscrap'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmenappear'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmandeathexplode')
    })

    def simulate_damage(self, x_position: int, y_position: int, target: GameObject) -> int:
        sorrounding_targets = list(self.attackable_tiles(target.x, target.y, range=1))
        sorrounding_targets.remove(target)

        return self.attack + (self.attack / 2) * len(sorrounding_targets)

    def attack_target(self, target: "Ninja") -> None:
        if target.hp <= 0:
            return

        # This seems to fix the mirror mode?
        time.sleep(0.25)

        self.attack_animation(target.x, target.y)
        target.set_health(target.hp - self.attack)

        tile = self.game.grid.get_tile(target.x, target.y)

        sorrounding_targets = list(self.attackable_tiles(target.x, target.y, range=1))
        sorrounding_targets.remove(tile)

        time.sleep(0.25)
        for sorrounding_target in sorrounding_targets:
            object = self.game.grid[sorrounding_target.x, sorrounding_target.y]
            object.set_health(object.hp - self.attack / 2)

    def idle_animation(self) -> None:
        self.animate_object(
            f'scrap_idle_anim',
            play_style='loop',
            register=False
        )

    def move_animation(self) -> None:
        self.animate_object(
            f'scrap_move_anim',
            play_style='loop',
            reset=True
        )
        self.idle_animation()

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
        time.sleep(1.1)
        self.impact_sound()

        # TODO: Snowball particle

    def ko_animation(self) -> None:
        self.animate_object(
            f'scrap_ko_anim',
            play_style='play_once',
            reset=True
        )
        self.ko_sound()

    def hit_animation(self) -> None:
        self.animate_object(
            f'scrap_hit_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

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

    assets = AssetCollection({
        Asset.from_name('tank_swipe_horiz_anim'),
        Asset.from_name('tank_swipe_vert_anim'),
        Asset.from_name('tank_idle_anim'),
        Asset.from_name('tank_attack_anim'),
        Asset.from_name('tank_hit_anim'),
        Asset.from_name('tank_move_anim'),
        Asset.from_name('tank_ko_anim'),
        Asset.from_name('tank_daze_anim'),
        Asset.from_name('snowman_spawn_anim')
    })
    sounds = SoundCollection({
        Sound.from_name('sfx_mg_2013_cjsnow_snowmantankhit'),
        Sound.from_name('sfx_mg_2013_cjsnow_footsteptank'),
        Sound.from_name('sfx_mg_2013_cjsnow_attacktank'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmenappear'),
        Sound.from_name('sfx_mg_2013_cjsnow_snowmandeathexplode')
    })

    def simulate_damage(self, x_position: int, y_position: int, target: GameObject) -> int:
        # Horizontal swipe
        if x_position == target.x:
            total_damage = self.attack

            left = self.game.grid[x_position-1, y_position]
            right = self.game.grid[x_position+1, y_position]

            if left is not None and not isinstance(left, Enemy):
                total_damage += self.attack / 2

            if right is not None and not isinstance(right, Enemy):
                total_damage += self.attack / 2

            return total_damage

        # Vertical swipe
        elif y_position == target.y:
            total_damage = self.attack

            above = self.game.grid[x_position, y_position-1]
            below = self.game.grid[x_position, y_position+1]

            if above is not None and not isinstance(above, Enemy):
                total_damage += self.attack / 2

            if below is not None and not isinstance(below, Enemy):
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

            if left is not None and not isinstance(left, Enemy):
                left.set_health(left.hp - self.attack / 2)

            if right is not None and not isinstance(right, Enemy):
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

            if above is not None and not isinstance(above, Enemy):
                above.set_health(above.hp - self.attack / 2)

            if below is not None and not isinstance(below, Enemy):
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

    def idle_animation(self) -> None:
        self.animate_object(
            f'tank_idle_anim',
            play_style='loop',
            register=False
        )

    def move_animation(self) -> None:
        self.animate_object(
            f'tank_move_anim',
            play_style='loop',
            reset=True
        )
        self.idle_animation()

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

        # TODO: Swipe effect

    def ko_animation(self) -> None:
        self.animate_object(
            f'tank_ko_anim',
            play_style='play_once',
            reset=True
        )
        self.ko_sound()

    def hit_animation(self) -> None:
        self.animate_object(
            f'tank_hit_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def hit_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_snowmantankhit')

    def attack_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attacktank')
