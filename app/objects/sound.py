
from ..engine.game import Game
from ..engine import Instance
from .asset import Asset

from dataclasses import dataclass

@dataclass
class Sound(Asset):
    looping: bool = False
    volume: int = 100
    radius: int = 0
    game_object_id: int = -1
    response_object_id: int = -1

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
        asset = Instance.sound_assets.by_index(index)

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
        asset = Instance.sound_assets.by_name(name)

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

    def play(self, game: Game) -> None:
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
