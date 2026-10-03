
from __future__ import annotations

from typing import TYPE_CHECKING, Generic
from collections.abc import Iterable
import logging

if TYPE_CHECKING:
    from ..engine.penguin import Penguin
    from ..engine.game import Game
    from .gameobject import GameObject
    from .asset import Asset
    from .ninjas import Ninja

from .collections_generic import LockedSet

class Players(LockedSet["Penguin"]):
    def by_id(self, id: int) -> Penguin | None:
        return next((player for player in self if player.pid == id), None)

    def by_name(self, name: str) -> Penguin | None:
        return next((player for player in self if player.name == name), None)

    def by_token(self, token: str) -> Penguin | None:
        return next((player for player in self if player.token == token), None)

    def with_id(self, id: int) -> list[Penguin]:
        return [player for player in self if player.pid == id]

    def with_name(self, name: str) -> list[Penguin]:
        return [player for player in self if player.name == name]

    def with_token(self, token: str) -> list[Penguin]:
        return [player for player in self if player.token == token]

    def with_element(self, element: str, battle_mode: int = 0) -> list[Penguin]:
        return [player for player in self if player.element == element and player.battle_mode == battle_mode]

class Games(LockedSet["Game"]):
    def add(self, item: Game) -> None:
        with self.lock:
            item.id = self.next_id()
            item.logger = logging.getLogger(f'Game ({item.id})')
            return super().add(item)

    def by_id(self, id: int) -> Game | None:
        return next((game for game in self if game.id == id), None)

    def with_player(self, player: Penguin) -> Game | None:
        return next((game for game in self if player in game.clients), None)

    def next_id(self) -> int:
        return max([game.id for game in self] or [0]) + 1

class AssetCollection(set["Asset"]):
    def __init__(self, initial_data: Iterable[Asset] = ()) -> None:
        super().__init__(initial_data)

    def by_index(self, index: int) -> Asset | None:
        return next((asset for asset in self if asset.index == index), None)

    def by_name(self, name: str) -> Asset | None:
        return next((asset for asset in self if asset.name == name), None)

class ObjectCollection(LockedSet["GameObject"]):
    def __init__(
        self,
        initial_data: Iterable[GameObject] = (),
        offset: int = 0
    ) -> None:
        super().__init__()
        super().update(initial_data)
        self.offset = offset

    def add(self, item: GameObject) -> None:
        with self.lock:
            item.id = self.get_id()
            return super().add(item)

    def update(self, *others: Iterable[GameObject]) -> None:
        with self.lock:
            for objects in others:
                for object in objects:
                    self.add(object)

    def by_id(self, id: int) -> GameObject | Ninja | None:
        return next((object for object in self if object.id == id), None)

    def by_name(self, name: str) -> GameObject | Ninja | None:
        return next((object for object in self if object.name == name), None)

    def by_name_required(self, name: str) -> GameObject | Ninja:
        result = self.by_name(name)
        assert result
        return result

    def with_id(self, id: int) -> list[GameObject | Ninja]:
        return [object for object in self if object.id == id]

    def with_name(self, name: str) -> list[GameObject | Ninja]:
        return [object for object in self if object.name == name]

    def get_id(self) -> int:
        return max([object.id for object in self] or [self.offset]) + 1
