
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.game import Game

import app.engine as Engine
from .asset import Asset

from dataclasses import dataclass

@dataclass
class Sound(Asset):
    looping: bool = False
    volume: int = 100
    radius: int = 0
    game_object_id: int = -1
    response_object_id: int = -1

    def __eq__(self, asset: "Asset") -> bool:
        return self.index == asset.index

    def __hash__(self) -> int:
        return hash(self.index)

    @classmethod
    def from_index(
        cls,
        index: int,
        looping: bool = False,
        volume: int = 100,
        radius: int = 0,
        game_object_id: int = -1,
        response_object_id: int = -1
    ) -> "Sound":
        asset = Engine.Instance.sound_assets.by_index(index)

        return Sound(
            asset.index,
            asset.name,
            asset.url,
            looping,
            volume,
            radius,
            game_object_id,
            response_object_id
        )

    @classmethod
    def from_name(
        cls,
        name: str,
        looping: bool = False,
        volume: int = 100,
        radius: int = 0,
        game_object_id: int = -1,
        response_object_id: int = -1
    ) -> "Sound":
        asset = Engine.Instance.sound_assets.by_name(name)

        return Sound(
            asset.index,
            asset.name,
            asset.url,
            looping,
            volume,
            radius,
            game_object_id,
            response_object_id
        )

    def play(self, game: "Game") -> None:
        game.send_tag(
            'FX_PLAYSOUND',
            f'0:{self.index}',
            0, # "handleId"
            int(self.looping),
            self.volume,
            self.game_object_id,
            self.radius,
            self.response_object_id
        )

        # TODO: Add callback handler for sound completion
        #       This can be done through the "handleId" parameter
