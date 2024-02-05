
from __future__ import annotations

from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass

if TYPE_CHECKING:
    from app.engine.penguin import Penguin
    from app.engine.game import Game

from app.engine.callbacks import ActionType
from app.objects.asset import Asset
from app import session

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
        asset = session.sound_assets.by_index(index)

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
        asset = session.sound_assets.by_name(name)

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

    def play(self, target: "Game" | "Penguin", object_id: int = -1, callback: Callable | None = None) -> None:
        try:
            handle_id = target.callbacks.register_action(
                self.name,
                ActionType.Sound,
                object_id,
                callback
            )
        except AttributeError:
            handle_id = -1

        target.send_tag(
            'FX_PLAYSOUND',
            f'0:{self.index}',
            handle_id,
            int(self.looping),
            self.volume,
            self.game_object_id,
            self.radius,
            self.response_object_id
        )

    def stop(self, target: "Game") -> None:
        if not (action := target.callbacks.by_name(self.name)):
            return

        target.send_tag(
            'FX_STOPSOUND',
            f'0:{action.handle_id}'
        )
