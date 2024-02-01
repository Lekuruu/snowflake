
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.game import Game
    from ..engine.penguin import Penguin
    from .gameobject import GameObject
    from .ninjas import Ninja
    from .sound import Sound
    from .asset import Asset

from typing import Set, List, Iterator, Iterable
from threading import Lock

import logging

class Players(Set["Penguin"]):
    def __init__(self):
        self.lock = Lock()
        super().__init__()

    def __iter__(self) -> Iterator["Penguin"]:
        with self.lock:
            players = iter(list(super().__iter__()))
        return players

    def __len__(self) -> int:
        with self.lock:
            return len(list(super().__iter__()))

    def __contains__(self, player: "Penguin") -> bool:
        with self.lock:
            return super().__contains__(player)

    def __repr__(self) -> str:
        with self.lock:
            return f'<Players ({len(self)})>'

    def add(self, player: "Penguin") -> None:
        return super().add(player)

    def remove(self, player: "Penguin") -> None:
        try:
            return super().remove(player)
        except (ValueError, KeyError):
            pass

    def by_id(self, id: int) -> "Penguin" | None:
        return next((player for player in self if player.pid == id), None)

    def by_name(self, name: str) -> "Penguin" | None:
        return next((player for player in self if player.name == name), None)

    def by_token(self, token: str) -> "Penguin" | None:
        return next((player for player in self if player.token == token), None)

    def with_id(self, id: int) -> List["Penguin"]:
        return [player for player in self if player.pid == id]

    def with_name(self, name: str) -> List["Penguin"]:
        return [player for player in self if player.name == name]

    def with_token(self, token: str) -> List["Penguin"]:
        return [player for player in self if player.token == token]

    def with_element(self, element: str) -> List["Penguin"]:
        return [player for player in self if player.element == element]

class Games(Set["Game"]):
    def __init__(self):
        self.lock = Lock()
        super().__init__()

    def __iter__(self) -> Iterator["Game"]:
        with self.lock:
            games = iter(list(super().__iter__()))
        return games

    def __len__(self) -> int:
        with self.lock:
            return len(list(super().__iter__()))

    def __contains__(self, game: "Game") -> bool:
        with self.lock:
            return super().__contains__(game)

    def __repr__(self) -> str:
        with self.lock:
            return f'<Games ({len(self)})>'

    def add(self, game: "Game") -> None:
        game.id = self.next_id()
        game.logger = logging.getLogger(f'Game ({game.id})')
        return super().add(game)

    def remove(self, game: "Game") -> None:
        try:
            return super().remove(game)
        except (ValueError, KeyError):
            pass

    def by_id(self, id: int) -> "Game" | None:
        return next((game for game in self if game.id == id), None)

    def with_player(self, player: "Penguin") -> "Game" | None:
        return next([game for game in self if player in game.clients], None)

    def next_id(self) -> int:
        return max([game.id for game in self] or [0]) + 1

class AssetCollection(Set["Asset"]):
    def __init__(self, initial_data: Iterable = {}) -> None:
        super().__init__()
        super().update(initial_data)

    def __eq__(self, other: "AssetCollection") -> bool:
        return super().__eq__(other)

    def __hash__(self) -> int:
        return hash(tuple(self))

    def add(self, asset: "Asset") -> None:
        return super().add(asset)

    def remove(self, asset: "Asset") -> None:
        return super().remove(asset)

    def by_index(self, index: int) -> "Asset" | None:
        return next((asset for asset in self if asset.index == index), None)

    def by_name(self, name: str) -> "Asset" | None:
        return next((asset for asset in self if asset.name == name), None)

class ObjectCollection(Set["GameObject"]):
    def __init__(self, initial_data: Iterable = {}) -> None:
        super().__init__()
        super().update(initial_data)

    def add(self, object: "GameObject", assign_id=True) -> None:
        if assign_id:
            object.id = self.get_id()

        return super().add(object)

    def update(self, objects: List["GameObject"], assign_ids=True) -> None:
        if assign_ids:
            for object in objects:
                object.id = self.get_id()

        super().update(objects)

    def remove(self, object: "GameObject") -> None:
        if object in self:
            return super().remove(object)

    def by_id(self, id: int) -> "GameObject" | Ninja | None:
        return next((object for object in self if object.id == id), None)

    def by_name(self, name: str) -> "GameObject" | Ninja | None:
        return next((object for object in self if object.name == name), None)

    def with_id(self, id: int) -> List["GameObject" | Ninja]:
        return [object for object in self if object.id == id]

    def with_name(self, name: str) -> List["GameObject" | Ninja]:
        return [object for object in self if object.name == name]

    def get_id(self) -> int:
        return max([object.id for object in self] or [0]) + 1

class SoundCollection(AssetCollection):
    def __init__(self, initial_data: Iterable = {}) -> None:
        super().__init__()
        super().update(initial_data)

    def by_index(self, index: int) -> "Sound" | None:
        return next((sound for sound in self if sound.index == index), None)

    def by_name(self, name: str) -> "Sound" | None:
        return next((sound for sound in self if sound.name == name), None)
