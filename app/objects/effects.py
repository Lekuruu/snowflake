
from __future__ import annotations

from typing import TYPE_CHECKING, List
from twisted.internet import reactor

if TYPE_CHECKING:
    from app.engine.game import Game

from app.data import MirrorMode, OriginMode
from app.objects import (
    AssetCollection,
    GameObject,
    Asset
)

import time

class Effect(GameObject):
    def __init__(
        self,
        game: "Game",
        name: str,
        x: int,
        y: int,
        x_offset: int = 0,
        y_offset: int = 0,
        origin_mode: OriginMode = OriginMode.NONE,
        mirror_mode: MirrorMode = MirrorMode.NONE,
        duration: int = 0
    ):
        super().__init__(
            game,
            name,
            x,
            y,
            x_offset=x_offset,
            y_offset=y_offset,
            origin_mode=origin_mode,
            mirror_mode=mirror_mode
        )
        self.duration = duration

    def play(self):
        self.place_object()
        self.place_sprite(self.name)

class AttackTile(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "ui_tile_attack",
            x,
            y,
            x_offset=0.5,
            y_offset=0.9998
        )

    def play(self, auto_remove=False):
        if not self.game.grid.is_valid(self.x, self.y):
            return

        self.place_object()
        self.place_sprite(self.name)

        if auto_remove:
            reactor.callLater(0.2, self.remove_object)

class HealTile(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "ui_tile_heal",
            x,
            y,
            x_offset=0.5,
            y_offset=0.9998
        )

    def play(self, auto_remove=False):
        if not self.game.grid.is_valid(self.x, self.y):
            return

        self.place_object()
        self.place_sprite(self.name)

        if auto_remove:
            reactor.callLater(0.2, self.remove_object)

class HealParticles(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "ui_healfx_anim",
            x,
            y,
            x_offset=0.50005,
            y_offset=1.0005,
            duration=0.737
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)
        self.animate_sprite(0, 10, duration=self.duration * 1000)
        reactor.callLater(self.duration, self.remove_object)

class AttackTileField:
    def __init__(self, game: "Game", center_x: int, center_y: int):
        self.game = game
        self.center_x = center_x
        self.center_y = center_y
        self.tiles = []

    def play(self):
        x_offsets = range(-1, 2)
        y_offsets = range(-1, 2)

        for x_offset in x_offsets:
            for y_offset in y_offsets:
                x = self.center_x + x_offset
                y = self.center_y + y_offset

                self.tiles.append(tile := AttackTile(self.game, x, y))
                tile.play()

        time.sleep(0.25)
        self.remove()

    def remove(self):
        for tile in self.tiles:
            tile.remove_object()

class DamageNumbers(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "ui_attack_numbers_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=0.9995,
            duration=0.5
        )

    def play(self, damage: int):
        frames = {
            3: (0, 4),
            4: (5, 9),
            5: (10, 14),
            6: (15, 19),
            8: (20, 24),
            9: (25, 29),
            10: (30, 34),
            11: (35, 39),
            12: (40, 44),
            15: (45, 49),
            18: (50, 54),
            20: (55, 59),
            22: (60, 64),
            24: (65, 69)
        }

        if not (range := frames.get(damage)):
            return

        self.place_object()
        self.place_sprite(self.name)
        self.animate_sprite(*range, duration=self.duration * 1000)
        reactor.callLater(self.duration, self.remove_object)

class HealNumbers(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "ui_heal_numbers_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=0.9995,
            duration=0.5
        )

    def play(self, hp: int):
        frames = {
            1: (0, 4),
            6: (5, 9),
            9: (10, 14),
            10: (15, 19),
            11: (20, 24),
            12: (25, 29)
        }

        if not (range := frames.get(hp)):
            return

        self.place_object()
        self.place_sprite(self.name)
        self.animate_sprite(*range, duration=self.duration * 1000)
        reactor.callLater(self.duration, self.remove_object)

class Explosion(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "effect_explosion_anim",
            x,
            y,
            x_offset=0.50005,
            y_offset=1.0005,
            duration=0.4
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)
        self.animate_sprite(0, 4, duration=self.duration * 260)
        reactor.callLater(self.duration, self.remove_object)

class SnowProjectile(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "snow_projectile",
            x,
            y,
            x_offset=0.5,
            y_offset=1,
            duration=0.2
        )

    def play(self, target_x: int, target_y: int):
        self.set_offset(target_x, target_y)
        self.place_object()

        self.set_mirror_mode(target_x, target_y)
        name = self.get_animation_name(target_x, target_y)

        self.place_sprite(name)
        self.move_object(
            target_x,
            target_y,
            duration=self.duration * 1000
        )

    def set_mirror_mode(self, target_x: int, target_y: int):
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if x_diff < 0 and y_diff > 0:
            self.mirror_mode = MirrorMode.XY

        elif x_diff < 0:
            self.mirror_mode = MirrorMode.X

        elif y_diff > 0:
            self.mirror_mode = MirrorMode.Y

    def set_offset(self, target_x: int, target_y: int):
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff <= 0:
            # Player is below the target
            self.y_offset = 2.2

        else:
            # Player is above the target
            self.y_offset = 1.5

        if x_diff < 0:
            # Player is behind the target
            self.x_offset = 1

        else:
            # Player is in front of the target
            self.x_offset = 0.5

    def get_animation_name(self, target_x: int, target_y: int) -> str:
        x_diff = abs(target_x - self.x)
        y_diff = abs(target_y - self.y)

        if x_diff > y_diff and y_diff == 0:
            return "snowninja_projectilehoriz_anim"

        if x_diff < y_diff and x_diff == 0:
            return "snowninja_projectilevert_anim"

        return "snowninja_projectileangle_anim"

class FireProjectile(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "fire_projectile",
            x,
            y,
            x_offset=0.5,
            y_offset=1
        )

    def play(self, target_x: int, target_y: int):
        self.set_offset(target_x, target_y)
        self.place_object()
        self.set_mirror_mode(target_x, target_y)

        name = self.get_animation_name(target_x, target_y)
        self.place_sprite(name)

    def set_mirror_mode(self, target_x: int, target_y: int):
        if (target_x - self.x) < 0:
            self.mirror_mode = MirrorMode.X

    def set_offset(self, target_x: int, target_y: int):
        if (target_x - self.x) < 0:
            self.x_offset = -1

    def get_animation_name(self, target_x: int, target_y: int) -> str:
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        distance = abs(self.x - target_x) + abs(self.y - target_y)

        if x_diff == 0 and y_diff < 0:
            return "fireninja_projectile_up_anim" if distance == 1 else "fireninja_projectile_upfar_anim"

        elif x_diff == 0 and y_diff > 0:
            return "fireninja_projectile_down_anim" if distance == 1 else "fireninja_projectile_downfar_anim"

        elif y_diff == 0:
            return "fireninja_projectile_right_anim" if distance == 1 else "fireninja_projectile_rightfar_anim"

        elif y_diff > 0:
            return "fireninja_projectile_angledown_anim"

        elif y_diff < 0:
            return "fireninja_projectile_angleup_anim"

        return "fireninja_projectile_right_anim"

class SlyProjectile(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "sly_projectile_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1,
            duration=0.5
        )

    def play(self, target_x: int, target_y: int):
        if self.x > target_x:
            self.x_offset = 1
            self.y_offset = 0.8

        self.place_object()
        self.place_sprite(self.name)

        self.x_offset = 0.5
        self.y_offset = 1
        self.move_object(target_x, target_y, duration=self.duration * 1000)

class ScrapImpact(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "scrap_attackeffect_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1,
            duration=0.4
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)
        reactor.callLater(self.duration, self.remove_object)

class ScrapImpactLittle(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "scrap_attacklittleeffect_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)

class ScrapImpactSurroundings:
    def __init__(self, game: "Game", center_x: int, center_y: int):
        self.game = game
        self.center_x = center_x
        self.center_y = center_y
        self.effects: List[Effect] = []

    def play(self):
        x_offsets = range(-1, 2)
        y_offsets = range(-1, 2)

        for x_offset in x_offsets:
            for y_offset in y_offsets:
                x = self.center_x + x_offset
                y = self.center_y + y_offset

                if not self.game.grid.is_valid(x, y):
                    continue

                self.effects.append(tile := AttackTile(self.game, x, y))
                self.effects.append(impact := ScrapImpactLittle(self.game, x, y))
                impact.play()
                tile.play()

        time.sleep(0.35)
        self.remove()

    def remove(self):
        for effect in self.effects:
            effect.remove_object()

class ScrapProjectile(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "scrap_projectile",
            x,
            y,
            x_offset=-0.25,
            y_offset=1.5
        )

    def play_east(self, target_x: int, target_y: int):
        if target_x < 0 or target_x > 8:
            return

        if target_y < 0 or target_y > 4:
            return

        self.place_object()
        self.place_sprite("scrap_projectileeast_anim")
        self.move_object(target_x, target_y, duration=180)

    def play_north(self, target_x: int, target_y: int):
        if target_x < 0 or target_x > 8:
            return

        if target_y < 0 or target_y > 4:
            return

        self.place_object()
        self.place_sprite("scrap_projectilenorth_anim")
        self.move_object(target_x, target_y, duration=180)

    def play_northeast(self, target_x: int, target_y: int):
        if target_x < 0 or target_x > 8:
            return

        if target_y < 0 or target_y > 4:
            return

        self.place_object()
        self.place_sprite("scrap_projectilenortheast_anim")
        self.move_object(target_x, target_y, duration=180)

class ScrapProjectileImpact:
    def __init__(self, game: "Game", center_x: int, center_y: int):
        self.game = game
        self.center_x = center_x
        self.center_y = center_y
        self.effects: List[ScrapProjectile] = []
        self.duration = 0.4

    def play(self):
        self.effects.append(projectile := ScrapProjectile(self.game, self.center_x, self.center_y))
        projectile.play_east(self.center_x + 1, self.center_y)

        self.effects.append(projectile := ScrapProjectile(self.game, self.center_x, self.center_y))
        projectile.play_east(self.center_x - 1, self.center_y)

        self.effects.append(projectile := ScrapProjectile(self.game, self.center_x, self.center_y))
        projectile.play_north(self.center_x, self.center_y - 0.8)

        self.effects.append(projectile := ScrapProjectile(self.game, self.center_x, self.center_y))
        projectile.play_north(self.center_x, self.center_y + 0.8)

        self.effects.append(projectile := ScrapProjectile(self.game, self.center_x, self.center_y))
        projectile.play_northeast(self.center_x + 1, self.center_y - 0.8)

        self.effects.append(projectile := ScrapProjectile(self.game, self.center_x, self.center_y))
        projectile.play_northeast(self.center_x - 1, self.center_y - 0.8)

        self.effects.append(projectile := ScrapProjectile(self.game, self.center_x, self.center_y))
        projectile.play_northeast(self.center_x + 1, self.center_y + 0.8)

        self.effects.append(projectile := ScrapProjectile(self.game, self.center_x, self.center_y))
        projectile.play_northeast(self.center_x - 1, self.center_y + 0.8)

        time.sleep(self.duration)
        for effect in self.effects:
            effect.remove_object()

class TankSwipeHorizontal(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "tank_swipe_horiz_anim",
            x,
            y,
            x_offset=0.5005,
            y_offset=1.005
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)
        self.animate_sprite(0, 6, duration=400)

class TankSwipeVertical(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "tank_swipe_vert_anim",
            x,
            y,
            x_offset=0.5005,
            y_offset=1.005
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)
        self.animate_sprite(0, 6, duration=400)

class WaterPowerBeam(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "waterninja_powercard_water_loop_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)

class FirePowerBeam(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "fireninja_powerskyfire_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1,
            duration=1.35
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)

class SnowPowerBeam(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "snowninja_beam_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1.55
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)

class SnowIgloo(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "snowninja_igloodrop",
            x,
            y,
            x_offset=0.5,
            y_offset=2,
            duration=2,
            origin_mode=OriginMode.BOTTOM_MIDDLE
        )

    def play(self, play_sound: bool = True):
        self.place_object()
        self.animate_object('snowninja_igloodrop_anim1', reset=True)
        self.animate_object('snowninja_igloodrop_anim2')
        self.animate_object('blank_png', play_style='loop')

        if play_sound:
            reactor.callLater(
                1.2, self.play_sound,
                'sfx_mg_2013_cjsnow_impactpowercardsnow'
            )

class WaterFishDrop(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "waterninja_powercard_fishdrop_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=2.4,
            duration=1.8,
            origin_mode=OriginMode.BOTTOM_MIDDLE
        )

    def play(self, **kwargs):
        self.place_object()
        self.animate_object(self.name)
        self.animate_sprite(0, 26, duration=1700)
        self.animate_object('blank_png')

class FirePowerBottle(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "fireninja_powerbottle_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=2,
            duration=1,
            origin_mode=OriginMode.BOTTOM_MIDDLE
        )

    def play(self, **kwargs):
        self.place_object()
        self.animate_object(self.name)
        self.animate_sprite(0, 16, duration=1060)
        self.animate_object('blank_png')

class Flame(Effect):
    def __init__(self, game: "Game", x: int, y: int) -> None:
        super().__init__(
            game,
            "effect_resisualfiredamage_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1.0025
        )
        self.rounds_left = 2

    def play(self):
        self.place_object()
        self.place_sprite(self.name)

class Shield(Effect):
    def __init__(self, game: "Game", x: int, y: int) -> None:
        super().__init__(
            game,
            "effect_shield",
            x,
            y,
            x_offset=0.5,
            y_offset=1.0015
        )

    def play(self):
        self.place_object()
        self.place_sprite('effect_shield_loop')

    def pop(self):
        self.place_object()
        self.place_sprite('effect_shieldpop_anim')
        self.animate_sprite(0, 3, duration=200)
        reactor.callLater(0.2, self.remove_object)

class Rage(Effect):
    def __init__(self, game: "Game", x: int, y: int) -> None:
        super().__init__(
            game,
            "effect_rage",
            x,
            y,
            x_offset=0.5,
            y_offset=1.0025
        )

    def play(self):
        self.place_object()
        self.place_sprite('effect_rageloop_anim')

    def use(self, x: int, y: int):
        self.move_object(x, y, duration=100)
        self.place_sprite('effect_ragehit_anim')
        self.animate_sprite(0, 11, duration=750)
        reactor.callLater(0.7, self.remove_object)

class MemberReviveBeam(Effect):
    def __init__(self, game: "Game", x: int, y: int) -> None:
        super().__init__(
            game,
            "effect_revivebeam_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1,
            origin_mode=OriginMode.BOTTOM_MIDDLE
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)
        self.animate_sprite(0, 29, duration=1200)

class TuskIcicle(Effect):
    def __init__(self, game: "Game", x: int, y: int) -> None:
        super().__init__(
            game,
            "tusk_icicle_drop_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)
        self.animate_sprite(0, 15, duration=800)
        reactor.callLater(0.8, self.apply_damage)

    def apply_damage(self) :
        target = self.game.grid[self.x, self.y]

        if not target:
            return

        if target.name not in ('Water', 'Fire', 'Snow'):
            return

        if target.hp <= 0:
            return

        target.set_health(target.hp - self.game.tusk.attack)
        self.remove_object()

class TuskIcicleRow:
    def __init__(self, game: "Game", row: int) -> None:
        self.first_row = row[0]
        self.second_row = row[1]
        self.game = game

    def play(self):
        x_range = list(self.game.grid.x_range)
        x_range.reverse()

        for x in x_range:
            TuskIcicle(self.game, x, self.first_row).play()
            TuskIcicle(self.game, x, self.second_row).play()
            time.sleep(0.09)

class TuskPushRock(Effect):
    def __init__(self, game: "Game", x: int, y: int) -> None:
        super().__init__(
            game,
            "effect_tusk_push",
            x,
            y,
            x_offset=0.5,
            y_offset=1,
            duration=0.75
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)
        self.animate_sprite(0, 14, duration=self.duration * 1000)
        reactor.callLater(self.duration, self.remove_object)
