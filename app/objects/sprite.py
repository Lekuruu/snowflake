
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.game import Game

from dataclasses import dataclass
from .asset import Asset

import app.engine as engine

@dataclass
class Sprite(Asset):
    game: "Game"

    @classmethod
    def from_index(cls, index: int, game: "Game") -> "Sprite":
        asset = engine.Instance.assets.by_index(index)

        return Sprite(
            asset.index,
            asset.name,
            asset.url,
            game
        )

    @classmethod
    def from_name(cls, name: str, game: "Game") -> "Sprite":
        asset = engine.Instance.assets.by_name(name)

        return Sprite(
            asset.index,
            asset.name,
            asset.url,
            game
        )

    def load(self) -> None:
        self.game.send_tag(
            'S_LOADSPRITE',
            f'0:{self.index}'
        )

    def animate(self) -> None:
        ...
