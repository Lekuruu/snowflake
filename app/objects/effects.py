
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.engine.game import Game

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
        x_offset: int = 0,
        y_offset: int = 0
    ):
        super().__init__(
            game,
            name,
            x,
            y,
            AssetCollection({Asset.from_name(name)}),
            x_offset=x_offset,
            y_offset=y_offset
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
