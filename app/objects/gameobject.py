
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .collections import SoundCollection
from ..engine import Instance
from .asset import Asset

if TYPE_CHECKING:
    from ..engine.game import Game

@dataclass
class GameObject:
    id: int
    name: str
    asset: Asset
    x: int
    y: int
    game: "Game"
    sounds: SoundCollection = SoundCollection()

    def initialize(self) -> None:
        blank_asset = Instance.assets.by_name('blank_png')

        self.game.send_tag(
            'O_HERE',
            self.id,
            f'0:{blank_asset.index}',
            self.x,
            self.y,
            0,  # TODO
            1,  # TODO
            0,  # TODO
            0,  # TODO
            0,  # TODO
            self.name,
            f'0:{blank_asset.index}',
            0,  # TODO
            1,  # TODO
            0   # TODO
        )

    def play_sound(self, sound_name: str) -> None:
        sound = self.sounds.by_name(sound_name)
        sound.play(self.game)
