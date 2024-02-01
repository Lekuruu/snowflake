
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.engine.game import Game

from ..data import MirrorMode, OriginMode
from .collections import AssetCollection
from .gameobject import GameObject
from .asset import Asset

class Effect(GameObject):
    def __init__(
        self,
        game: "Game",
        name: str,
        x: int,
        y: int,
        assets: AssetCollection | None = None,
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
            assets or AssetCollection({Asset.from_name(name)}),
            x_offset=x_offset,
            y_offset=y_offset,
            origin_mode=origin_mode,
            mirror_mode=mirror_mode
        )

    def play(self):
        self.place_object()
        self.place_sprite(self.name)
        self.animate_sprite()

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

class SnowProjectile(Effect):
    def __init__(self, game: "Game", x: int, y: int):
        super().__init__(
            game,
            "snow_projectile",
            x,
            y,
            AssetCollection({
                Asset.from_name("snowninja_projectileangle_anim"),
                Asset.from_name("snowninja_projectilehoriz_anim"),
                Asset.from_name("snowninja_projectilevert_anim")
            })
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
            self.y_offset = 2.25

        else:
            self.y_offset = 1

        if x_diff == 0:
            self.x_offset = 0.5

        elif x_diff < 0:
            self.x_offset = 1.5

    def get_animation_name(self, target_x: int, target_y: int) -> str:
        x_diff = abs(target_x - self.x)
        y_diff = abs(target_y - self.y)

        if x_diff > y_diff and y_diff == 0:
            return "snowninja_projectilehoriz_anim"

        if x_diff < y_diff and x_diff == 0:
            return "snowninja_projectilevert_anim"

        return "snowninja_projectileangle_anim"
