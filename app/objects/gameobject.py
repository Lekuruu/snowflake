
from dataclasses import dataclass
from typing import TYPE_CHECKING
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

    def initialize(self) -> None:
        blank_asset = Instance.assets.by_name('blank_png')

        for client in self.game.clients:
            client.send_tag(
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
