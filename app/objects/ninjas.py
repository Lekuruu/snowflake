
from __future__ import annotations

from typing import TYPE_CHECKING, List, Iterator
from twisted.internet import reactor

if TYPE_CHECKING:
    from app.engine.penguin import Penguin
    from app.engine.game import Game

from app.objects.target import Target, TuskTarget
from app.data import MirrorMode, TipPhase, Card
from app.objects.effects import (
    WaterPowerBeam,
    SnowPowerBeam,
    FirePowerBeam,
    FirePowerBottle,
    SnowProjectile,
    FireProjectile,
    HealParticles,
    DamageNumbers,
    WaterFishDrop,
    HealNumbers,
    AttackTile,
    SnowIgloo,
    Shield,
    Rage
)

from app.objects.enemies import Enemy, Tusk
from app.objects import GameObject

import app.engine.cards
import time

class Ninja(GameObject):
    name: str = 'Ninja'
    max_hp: int = 0
    range: int = 0
    attack: int = 0
    move: int = 0
    move_duration: int = 600

    def __init__(
        self,
        client: "Penguin",
        x: int = -1,
        y: int = -1
    ) -> None:
        super().__init__(
            client.game,
            self.__class__.name,
            x, y,
            grid=True,
            x_offset=0.5,
            y_offset=1
        )
        self.attack = self.__class__.attack
        self.range = self.__class__.range
        self.max_hp = self.__class__.max_hp
        self.hp = self.__class__.max_hp
        self.client = client
        self.targets: List["Target"] = []
        self.heals: int = 0

        self.ghost = GameObject(
            self.game,
            f'{self.name.lower()}ninja_move_ghost',
            x=-1,
            y=-1,
            on_click=self.on_ghost_click,
            grid=True,
            x_offset=0.5,
            y_offset=1
        )

        self.health_bar = GameObject(
            self.game,
            'reghealthbar_animation',
            x=self.x,
            y=self.y,
            x_offset=0.5,
            y_offset=1.005
        )

        self.shield: Shield | None = None
        self.rage: Rage | None = None

    @property
    def selected_target(self) -> "Target" | None:
        return next((target for target in self.targets if target.selected), None)

    @property
    def selected_object(self) -> GameObject | None:
        return self.selected_target.object if self.selected_target else None

    @property
    def placed_ghost(self) -> bool:
        return self.ghost.x != -1 and self.ghost.y != -1

    @property
    def is_reviving(self) -> bool:
        return isinstance(self.selected_object, Ninja) and self.selected_object.hp <= 0

    def remove_object(self) -> None:
        self.health_bar.remove_object()
        self.ghost.remove_object()
        super().remove_object()

    def move_object(self, x: int, y: int, duration: int | None = None) -> None:
        duration = duration or self.move_duration

        self.health_bar.move_object(x, y, duration)
        super().move_object(x, y, duration)
        self.ghost.x = x
        self.ghost.y = y

        if self.shield:
            self.shield.move_object(x, y, duration)

        if self.rage:
            self.rage.move_object(x, y, duration)

    def move_ninja(self, x: int, y: int) -> None:
        if self.hp <= 0 or self.client.disconnected:
            return

        if self.x == x and self.y == y:
            return

        if x == -1 or y == -1:
            return

        for ninja in self.game.ninjas:
            if not ninja.selected_object:
                continue

            if ninja.selected_target.object == self:
                ninja.selected_target.move_object(x, y)

        self.move_animation()
        self.move_object(x, y)
        self.move_sound()

        # Reset ghost position
        self.ghost.x = -1
        self.ghost.y = -1

    def place_healthbar(self) -> None:
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

    def set_health(self, hp: int, show_effects=True) -> None:
        if hp < self.hp and self.shield:
            self.shield.pop()
            self.shield = None
            return

        if self.client.disconnected and self.hp <= 0:
            return

        hp = max(0, min(hp, self.max_hp))
        self.animate_healthbar(self.hp, hp, duration=500)

        if hp >= self.hp:
            # Ninja gained health
            HealNumbers(
                self.game,
                self.x,
                self.y
            ).play(hp - self.hp)
            self.revive_animation()
            self.hp = hp
            return

        if show_effects:
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

        if hp > 0:
            self.hit_animation()
            self.client.update_cards()
            self.hp = hp
            return

        if self.hp <= 0:
            # Ninja is already KO
            return

        # Ninja was KO'd
        self.hp = hp
        self.targets = []
        self.ko_animation()

        if self.rage:
            self.rage.remove_object()

        if not self.client.disconnected:
            self.client.was_ko = True
            self.client.update_cards()
            self.ko_sound()

        # Check if any ninjas are still in healing state
        for ninja in self.game.ninjas:
            if ninja.selected_object == self:
                ninja.targets = []

    def place_ghost(self, x: int, y: int) -> None:
        if self.client.is_ready:
            return

        if not self.game.timer.running:
            return

        if self.hp <= 0:
            self.hide_ghost()
            return

        if (self.ghost.x == x) and (self.ghost.y == y):
            self.hide_ghost()
            self.show_targets()
            return

        if not self.game.grid.can_move(x, y):
            return

        self.game.grid.move(self.ghost, x, y)
        self.ghost.place_object()
        self.ghost.place_sprite(self.ghost.name)
        self.ghost.play_sound('sfx_mg_2013_cjsnow_uiselecttile')
        self.show_targets()

    def hide_ghost(self, reset_positions: bool = True) -> None:
        self.game.grid.remove(self.ghost)
        self.ghost.hide()

        if reset_positions:
            self.ghost.x = -1
            self.ghost.y = -1

    def on_ghost_click(self, client, object: GameObject, *args) -> None:
        if client.ninja != self:
            return

        if client.is_ready:
            return

        if client.selected_card:
            client.selected_card.place(object.x, object.y)
            return

        if self.client.selected_member_card:
            return

        self.hide_ghost()
        self.show_targets()

    def show_targets(self) -> None:
        self.remove_targets()

        healable_tiles = self.healable_tiles(
            self.x if not self.placed_ghost else self.ghost.x,
            self.y if not self.placed_ghost else self.ghost.y
        )

        for tile in healable_tiles:
            self.targets.append(target := Target(self, tile.x, tile.y))
            target.show_heal()

        attackable_tiles = self.attackable_tiles(
            self.x if not self.placed_ghost else self.ghost.x,
            self.y if not self.placed_ghost else self.ghost.y
        )

        for tile in attackable_tiles:
            target_object = self.game.grid[tile.x, tile.y]

            if isinstance(target_object, Tusk):
                self.targets.append(target := TuskTarget(self, tile.x, tile.y))
                target.show_attack()
                return

            self.targets.append(target := Target(self, tile.x, tile.y))
            target.show_attack()

    def hide_targets(self) -> None:
        for target in self.targets:
            target.hide()

    def remove_targets(self) -> None:
        for target in self.targets:
            target.remove_object()

        self.targets = []

    def attack_target(self, target: Enemy):
        # This delay seems to fix the mirror mode?
        time.sleep(0.25)

        self.attack_animation(target.x, target.y)
        self.client.update_cards()

        if self.rage:
            self.rage.use(target.x, target.y)
            self.rage = None

            target.set_health(
                target.hp - self.attack * 1.5
            )
            return

        target.set_health(
            target.hp - self.attack
        )

    def heal_target(self, target: "Ninja"):
        if self.client.last_tip == TipPhase.HEAL:
            self.game.hide_tip(self.client)

        if target.hp <= 0:
            self.revive_other_animation()
            return

        if self.name != 'Snow':
            return

        self.heals += 1
        self.heal_animation()
        self.client.update_cards()
        time.sleep(0.4)

        if self.rage:
            self.rage.use(target.x, target.y)
            self.rage = None

            target.set_health(
                target.hp + self.attack * 1.5
            )
            return

        target.set_health(
            target.hp + self.attack
        )

    def tiles_in_range(self) -> Iterator[GameObject]:
        for tile in self.game.grid.tiles:
            distance = self.game.grid.distance(
                (self.x, self.y),
                (tile.x, tile.y)
            )

            if distance <= self.move:
                yield tile

    def ghost_tiles_in_range(self) -> Iterator[GameObject]:
        if not self.placed_ghost:
            for tile in self.tiles_in_range():
                yield tile
            return

        for tile in self.game.grid.tiles:
            distance = self.game.grid.distance(
                (self.ghost.x, self.ghost.y),
                (tile.x, tile.y)
            )

            if distance <= self.move:
                yield tile

    def movable_tiles(self) -> Iterator[GameObject]:
        for tile in self.tiles_in_range():
            if not self.game.grid.can_move(tile.x, tile.y):
                continue

            yield tile

    def movable_ghost_tiles(self) -> Iterator[GameObject]:
        if not self.placed_ghost:
            for tile in self.movable_tiles():
                yield tile
            return

        for tile in self.ghost_tiles_in_range():
            if not self.game.grid.can_move(tile.x, tile.y):
                continue

            yield tile

    def attackable_tiles(self, target_x: int, target_y: int) -> Iterator[Enemy]:
        if self.hp <= 0:
            return []

        for tile in self.game.grid.tiles:
            target_object = self.game.grid[tile.x, tile.y]

            if not isinstance(target_object, Enemy):
                continue

            distance = abs(tile.x - target_x) + abs(tile.y - target_y)

            if distance <= self.range:
                yield tile

            if target_object.tile_range <= 0:
                continue

            # Enemy has a bigger tile range to be attacked from
            # Check if the ninja can attack in that range
            surrounding_tiles = self.game.grid.surrounding_tiles(
                center_x=tile.x,
                center_y=tile.y,
                distance=target_object.tile_range
            )

            for surrounding_tile in surrounding_tiles:
                distance = (
                    abs(surrounding_tile.x - target_x) +
                    abs(surrounding_tile.y - target_y)
                )

                if distance <= self.range:
                    yield tile

    def healable_tiles(self, target_x: int, target_y: int) -> Iterator["Ninja"]:
        if self.hp <= 0:
            return []

        for ninja in self.game.ninjas:
            if ninja.client.disconnected:
                continue

            if ninja == self:
                # Ninja cannot heal itself
                continue

            if ninja.hp == ninja.max_hp:
                # Ninja is already at full health
                continue

            if ninja.hp > 0 and self.name == 'Snow':
                # Only snow can heal ninjas that are not dead
                distance = self.game.grid.distance(
                    (ninja.x, ninja.y),
                    (target_x, target_y)
                )

                if distance <= self.range:
                    yield self.game.grid.get_tile(ninja.x, ninja.y)

            else:
                if ninja.hp > 0:
                    continue

                # Ninja is dead, limit range to surrounding tiles
                tiles = self.game.grid.surrounding_tiles(ninja.x, ninja.y)
                current_tile = self.game.grid.get_tile(target_x, target_y)

                if current_tile in tiles:
                    yield self.game.grid.get_tile(ninja.x, ninja.y)

    def place_powercard(self, x: int, y: int) -> None:
        if not self.game.timer.running:
            return

        if self.client.is_ready:
            return

        if isinstance(x, float) or isinstance(y, float):
            return

        if not self.game.grid.is_valid(x, y):
            return

        if self.hp <= 0:
            return

        tile = self.game.grid.get_tile(x, y)

        if tile not in self.ghost_tiles_in_range():
            return

        self.client.selected_card.place(x, y)

    def use_powercard(self, is_combo=False) -> None:
        if not self.client.selected_card:
            return

        self.client.selected_card.use(is_combo)

    """Animations"""

    def idle_animation(self) -> None:
        ...

    def move_animation(self) -> None:
        ...

    def ko_animation(self) -> None:
        ...

    def attack_animation(self, x: int, y: int) -> None:
        ...

    def win_animation(self) -> None:
        ...

    def hit_animation(self) -> None:
        ...

    def heal_animation(self) -> None:
        ...

    def revive_animation(self) -> None:
        ...

    def revive_other_animation(self) -> None:
        ...

    def revive_other_animation_loop(self) -> None:
        ...

    def revive_membercard_animation(self) -> None:
        ...

    def power_animation(self) -> None:
        ...

    """Sounds"""

    def ko_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_penguinground')

    def move_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_footsteppenguin')

    def attack_sound(self) -> None:
        ...

    def powercard_sound(self) -> None:
        ...

class WaterNinja(Ninja):
    name: str = 'Water'
    max_hp: int = 40
    range: int = 1
    attack: int = 10
    move: int = 2

    def idle_animation(self) -> None:
        self.animate_object(
            'waterninja_idle_anim',
            play_style='loop',
            register=False
        )

    def move_animation(self) -> None:
        self.animate_object(
            'waterninja_move_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def ko_animation(self) -> None:
        self.animate_object(
            'waterninja_kostart_anim',
            play_style='play_once',
            reset=True
        )
        self.animate_object(
            'waterninja_koloop_anim',
            play_style='loop'
        )

    def hit_animation(self) -> None:
        self.animate_object(
            'waterninja_hit_anim',
            play_style='play_once',
            reset=True
        )

        if self.is_reviving:
            self.revive_other_animation_loop()
            return

        self.idle_animation()

    def attack_animation(self, x: int, y: int) -> None:
        if self.x > x:
            self.mirror_mode = MirrorMode.X

        self.animate_object(
            'waterninja_attack_anim',
            play_style='play_once',
            callback=self.reset_sprite_settings,
            reset=True
        )
        self.idle_animation()

        time.sleep(0.45)
        self.attack_sound()

    def win_animation(self) -> None:
        self.animate_object(
            'waterninja_celebrate_anim',
            play_style='ping_pong',
            reset=True
        )

    def revive_animation(self) -> None:
        self.animate_object(
            f'waterninja_revived_anim',
            play_style='play_once',
            reset=True
        )
        HealParticles(self.game, self.x, self.y).play()

        if self.is_reviving:
            self.revive_other_animation_loop()
            return

        self.idle_animation()

    def revive_other_animation(self) -> None:
        self.animate_object(
            'waterninja_revive_other_intro_anim',
            play_style='play_once',
            reset=True
        )
        self.animate_object(
            'waterninja_revive_other_loop_anim',
            play_style='loop'
        )

    def revive_other_animation_loop(self) -> None:
        self.animate_object(
            'waterninja_revive_other_loop_anim',
            play_style='loop'
        )

    def revive_membercard_animation(self) -> None:
        self.animate_object(
            'waterninja_member_revive',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def power_animation(self) -> None:
        self.animate_object(
            'waterninja_powercard_summon_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()
        self.powercard_sound()
        time.sleep(0.65)

    def attack_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attackwater')

    def powercard_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attackpowercardwater')

class SnowNinja(Ninja):
    name: str = 'Snow'
    max_hp: int = 25
    range: int = 3
    attack: int = 6
    move: int = 3

    def idle_animation(self) -> None:
        self.animate_object(
            'snowninja_idle_anim',
            play_style='loop',
            register=False
        )

    def move_animation(self) -> None:
        self.animate_object(
            'snowninja_move_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def ko_animation(self) -> None:
        self.animate_object(
            'snowninja_kostart_anim',
            play_style='play_once',
            reset=True
        )
        self.animate_object(
            'snowninja_koloop_anim',
            play_style='loop'
        )

    def hit_animation(self) -> None:
        self.animate_object(
            'snowninja_hit_anim',
            play_style='play_once',
            reset=True
        )

        if self.is_reviving:
            self.revive_other_animation_loop()
            return

        self.idle_animation()

    def attack_animation(self, x: int, y: int) -> None:
        if self.x > x:
            self.mirror_mode = MirrorMode.X

        self.attack_sound()
        self.animate_object(
            'snowninja_attack_anim',
            play_style='play_once',
            callback=self.reset_sprite_settings,
            reset=True
        )
        self.idle_animation()

        time.sleep(0.3)
        self.projectile_animation(x, y)

    def projectile_animation(self, x: int, y: int) -> None:
        # This is kinda jank lol
        projectile = SnowProjectile(self.game, self.x, self.y)
        projectile.play(x, y)
        time.sleep(0.2)
        projectile.remove_object()

        projectile = SnowProjectile(self.game, self.x, self.y)
        projectile.play(x, y)
        self.do_later(0.2, projectile.remove_object)

    def heal_animation(self) -> None:
        self.animate_object(
            'snowninja_heal_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def win_animation(self) -> None:
        self.animate_object(
            'snowninja_celebrate_anim',
            play_style='ping_pong',
            reset=True
        )

    def revive_animation(self) -> None:
        self.animate_object(
            'snowninja_revive_anim',
            play_style='play_once',
            reset=True
        )
        HealParticles(self.game, self.x, self.y).play()

        if self.is_reviving:
            self.revive_other_animation_loop()
            return

        self.idle_animation()

    def revive_other_animation(self) -> None:
        self.animate_object(
            'snowninja_reviveothersintro_anim',
            play_style='play_once',
            reset=True
        )
        self.animate_object(
            'snowninja_reviveothersloop_anim',
            play_style='loop'
        )

    def revive_other_animation_loop(self) -> None:
        self.animate_object(
            'snowninja_reviveothersloop_anim',
            play_style='loop'
        )

    def revive_membercard_animation(self) -> None:
        self.animate_object(
            'snowninja_member_revive',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def power_animation(self) -> None:
        self.animate_object(
            'snowninja_powercard_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()
        self.powercard_sound()
        time.sleep(0.45)

    def attack_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attacksnow')

    def powercard_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attackpowercardsnow')

class FireNinja(Ninja):
    name: str = 'Fire'
    max_hp: int = 30
    range: int = 2
    attack: int = 8
    move: int = 2

    def idle_animation(self) -> None:
        self.animate_object(
            'fireninja_idle_anim',
            play_style='loop',
            register=False
        )

    def move_animation(self) -> None:
        self.animate_object(
            'fireninja_move_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def ko_animation(self) -> None:
        self.animate_object(
            'fireninja_kostart_anim',
            play_style='play_once',
            reset=True
        )
        self.animate_object(
            'fireninja_koloop_anim',
            play_style='loop'
        )

    def hit_animation(self) -> None:
        self.animate_object(
            'fireninja_hit_anim',
            play_style='play_once',
            reset=True
        )

        if self.is_reviving:
            self.revive_other_animation_loop()
            return

        self.idle_animation()

    def attack_animation(self, x: int, y: int) -> None:
        if self.x > x:
            self.mirror_mode = MirrorMode.X

        self.attack_sound()
        self.animate_object(
            'fireninja_attack_anim',
            play_style='play_once',
            callback=self.reset_sprite_settings,
            reset=True
        )
        self.idle_animation()

        time.sleep(1.45)
        self.projectile_animation(x, y)

    def projectile_animation(self, x: int, y: int) -> None:
        projectile = FireProjectile(self.game, self.x, self.y)
        projectile.play(x, y)
        self.do_later(0.25, projectile.remove_object)

    def win_animation(self) -> None:
        self.animate_object(
            'fireninja_celebratestart_anim',
            play_style='play_once',
            reset=True
        )
        self.animate_object(
            'fireninja_celebrateloop_anim',
            play_style='loop'
        )

    def revive_animation(self) -> None:
        self.animate_object(
            'fireninja_revived_anim',
            play_style='play_once',
            reset=True
        )
        HealParticles(self.game, self.x, self.y).play()

        if self.is_reviving:
            self.revive_other_animation_loop()
            return

        self.idle_animation()

    def revive_other_animation(self) -> None:
        self.animate_object(
            'fireninja_reviveother_anim',
            play_style='play_once',
            reset=True
        )
        self.animate_object(
            'fireninja_reviveotherloop_anim',
            play_style='loop'
        )

    def revive_other_animation_loop(self) -> None:
        self.animate_object(
            'fireninja_reviveotherloop_anim',
            play_style='loop'
        )

    def revive_membercard_animation(self) -> None:
        self.animate_object(
            'fireninja_member_revive',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()

    def power_animation(self) -> None:
        self.animate_object(
            'fireninja_power_anim',
            play_style='play_once',
            reset=True
        )
        self.idle_animation()
        self.powercard_sound()
        time.sleep(1)

    def move_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_footsteppenguinfire')

    def attack_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attackfire')

    def powercard_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_attackpowercardfire')

class Sensei(GameObject):
    name: str = 'Sensei'

    def __init__(self, game: Game, x: int, y: int) -> None:
        super().__init__(
            game,
            self.__class__.name,
            x, y,
            grid=True,
            x_offset=0.5,
            y_offset=1
        )

        self.element_state = 'snow'
        self.power_state = 0

    @property
    def next_element(self) -> str:
        return {
            'snow': 'fire',
            'fire': 'water',
            'water': 'snow'
        }[self.element_state]

    def update_state(self) -> None:
        self.power_state += 1

        if self.power_state >= 4:
            # Reset power state
            self.power_state = 1
            self.element_state = self.next_element

        action = {
            0: lambda: self.idle_animation(),
            1: lambda: self.idle_animation(),
            2: lambda: self.powerup_animation(),
            3: lambda: self.do_powerup()
        }

        action[self.power_state]()

    def do_powerup(self) -> None:
        if not self.game.enemies:
            return

        time.sleep(0.5)
        self.attack_animation()
        self.attack_sound()
        time.sleep(0.5)

        beam_class = {
            'fire': FirePowerBeam,
            'water': WaterPowerBeam,
            'snow': SnowPowerBeam
        }[self.element_state]

        beam_offset = {
            'fire': (0.6, 0.2),
            'water': (0.4, 1),
            'snow': (0.75, 1)
        }[self.element_state]

        beam = beam_class(self.game, self.x, self.y)
        beam.x_offset = beam_offset[0]
        beam.y_offset = beam_offset[1]
        beam.play()
        time.sleep(0.65)

        positions = [
            (1, 2),
            (4, 2),
            (7, 2)
        ]

        impacts = []
        delay = 0.35

        for x, y in positions:
            impacts.append(self.place_card(x, y))
            time.sleep(delay)

        if self.element_state == 'snow':
            self.snow_impact_sound()

        time.sleep(impacts[0][1].duration - delay)

        beam.remove_object()
        self.idle_animation()

        is_combo = len([
            ninja for ninja in self.game.ninjas
            if ninja.client.placed_powercard
        ]) > 0

        for card, impact in impacts:
            impact.remove_object()
            card.apply_health()

            if is_combo:
                card.apply_effects()

        self.game.wait_for_animations()

    def place_card(self, x: int, y: int):
        card = app.engine.cards.CardObject(
            Card(
                element=self.element_state[0],
                value=10
            ), self
        )
        card.object.x = x
        card.object.y = y

        impact_class = {
            'fire': FirePowerBottle,
            'water': WaterFishDrop,
            'snow': SnowIgloo
        }[self.element_state]

        impact = impact_class(self.game, x, y)
        impact.play(play_sound=False)
        return card, impact

    def idle_animation(self) -> None:
        self.animate_object(
            'sensei_idle_anim',
            play_style='loop',
            register=False
        )

    def win_animation(self) -> None:
        self.animate_object(
            'sensei_win_anim',
            play_style='play_once',
            reset=True
        )

    def lose_animation(self) -> None:
        self.animate_object(
            'sensei_lose_anim',
            play_style='play_once',
            reset=True
        )

    def attack_animation(self) -> None:
        self.animate_object(
            'sensei_attackstart_anim',
            play_style='play_once',
            duration=500,
            reset=True
        )
        self.animate_object(
            'sensei_attackloop_anim',
            play_style='loop'
        )

    def powerup_animation(self) -> None:
        start_animation = {
            'snow': 'sensei_powerupsnow_anim',
            'fire': 'sensei_powerupfire_anim',
            'water': 'sensei_powerupwater_anim'
        }[self.element_state]

        self.animate_object(
            start_animation,
            play_style='play_once',
            reset=True
        )

        loop_animation = {
            'snow': 'sensei_powerupsnowloop_anim',
            'fire': 'sensei_powerupfireloop_anim',
            'water': 'sensei_powerupwaterloop_anim'
        }[self.element_state]

        self.animate_object(
            loop_animation,
            play_style='loop'
        )

        self.animate_sprite(
            0, 5,
            play_style='loop',
            duration=600
        )

    def attack_sound(self) -> None:
        self.play_sound({
            'snow': 'sfx_mg_2013_cjsnow_attacksenseisnow',
            'fire': 'sfx_mg_2013_cjsnow_attacksenseifire',
            'water': 'sfx_mg_2013_cjsnow_attacksenseiwater'
        }[self.element_state])

    def hit_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_hitsensei')

    def snow_impact_sound(self) -> None:
        self.play_sound('sfx_mg_2013_cjsnow_impactsenseisnow')
