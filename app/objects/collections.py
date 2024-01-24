
from __future__ import annotations

from ..engine.penguin import Penguin
from .asset import Asset

from typing import Set, List, Iterator
from threading import Lock

class Players(Set[Penguin]):
    def __init__(self):
        self.lock = Lock()
        super().__init__()

    def __iter__(self) -> Iterator[Penguin]:
        with self.lock:
            players = iter(list(super().__iter__()))
        return players

    def __len__(self) -> int:
        with self.lock:
            return len(list(super().__iter__()))

    def __contains__(self, player: Penguin) -> bool:
        with self.lock:
            return super().__contains__(player)

    def __repr__(self) -> str:
        with self.lock:
            return f'<Players ({len(self)})>'

    def add(self, player: Penguin) -> None:
        return super().add(player)

    def remove(self, player: Penguin) -> None:
        try:
            return super().remove(player)
        except (ValueError, KeyError):
            pass

    def by_id(self, id: int) -> Penguin | None:
        return next((player for player in self if player.pid == id), None)

    def by_name(self, name: str) -> Penguin | None:
        return next((player for player in self if player.name == name), None)

    def by_token(self, token: str) -> Penguin | None:
        return next((player for player in self if player.token == token), None)

    def with_id(self, id: int) -> List[Penguin]:
        return [player for player in self if player.pid == id]

    def with_name(self, name: str) -> List[Penguin]:
        return [player for player in self if player.name == name]

    def with_token(self, token: str) -> List[Penguin]:
        return [player for player in self if player.token == token]

    def with_element(self, element: str) -> List[Penguin]:
        return [player for player in self if player.element == element]

class AssetCollection(Set[Asset]):
    def __init__(self) -> None:
        super().__init__()

    def add(self, asset: Asset) -> None:
        return super().add(asset)

    def remove(self, asset: Asset) -> None:
        return super().remove(asset)

    def by_index(self, index: int) -> Asset | None:
        return next((asset for asset in self if asset.index == index), None)

    def by_name(self, name: str) -> Asset | None:
        return next((asset for asset in self if asset.name == name), None)
