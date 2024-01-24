
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.game import Game

from dataclasses import dataclass
from .asset import Asset

@dataclass
class Sprite(Asset):
    game: "Game"

    @classmethod
    def from_index(cls, index: int, game: "Game") -> "Sprite":
        return cls(
            index,
            game
        )

    @classmethod
    def from_name(cls, name: str, game: "Game") -> "Sprite":
        return cls(
            game.assets.by_name(name).index,
            game
        )

    def load(self) -> None:
        self.game.send_tag(
            'S_LOADSPRITE',
            f'0:{self.index}'
        )

    def animate(self) -> None:
        ...
