
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
        mirror_mode: MirrorMode = MirrorMode.NONE
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

    def play(self):
        if not self.game.grid.is_valid(self.x, self.y):
            return

        self.place_object()
        self.place_sprite(self.name)

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

    def play(self):
        self.place_object()
        self.place_sprite(self.name)

class HealParticles(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "ui_healfx_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)
        self.animate_sprite(0, 10, duration=737)
        time.sleep(0.737)
        self.remove_object()

class Explosion(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "effect_explosion_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)
        reactor.callLater(0.4, self.remove_object)

class SnowProjectile(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "snow_projectile",
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
        self.move_object(
            target_x,
            target_y,
            duration=200
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
            y_offset=1
        )

    def play(self, target_x: int, target_y: int):
        if self.x > target_x:
            self.x_offset = 1
            self.y_offset = 0.8

        self.place_object()
        self.place_sprite(self.name)

        self.x_offset = 0.5
        self.y_offset = 1
        self.move_object(target_x, target_y, duration=500)

class ScrapImpact(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "scrap_attackeffect_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)
        reactor.callLater(0.4, self.remove_object)

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

        time.sleep(0.4)
        for effect in self.effects:
            effect.remove_object()

class TankSwipeHorizontal(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "tank_swipe_horiz_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)

class TankSwipeVertical(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "tank_swipe_vert_anim",
            x,
            y,
            x_offset=0.5,
            y_offset=1
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)
