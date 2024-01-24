
from dataclasses import dataclass
from ..engine.game import Game
from .asset import Asset

@dataclass
class Sprite(Asset):
    game: Game

    def load(self) -> None:
        self.game.send_tag(
            'S_LOADSPRITE',
            f'0:{self.index}'
        )

    def animate(self) -> None:
        ...
