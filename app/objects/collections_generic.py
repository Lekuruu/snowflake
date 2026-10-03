
from __future__ import annotations

from collections.abc import Iterable, Iterator
from collections.abc import Set as AbstractSet
from threading import RLock
from typing import TYPE_CHECKING, Generic, TypeVar

T = TypeVar('T')

class LockedSet(set[T], Generic[T]):
    """A thread-safe set implementation."""

    def __init__(self):
        self.lock = RLock()
        super().__init__()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} ({len(self)})>'

    def __iter__(self) -> Iterator[T]:
        with self.lock:
            items = iter(list(super().__iter__()))
        return items

    def __len__(self) -> int:
        with self.lock:
            return super().__len__()

    def __contains__(self, item: object) -> bool:
        with self.lock:
            return super().__contains__(item)

    def __iand__(self, other: AbstractSet[object]) -> LockedSet[T]:
        with self.lock:
            super().__iand__(other)
            return self

    def __ior__(self, other: AbstractSet[T]) -> LockedSet[T]:  # type: ignore[override,misc]
        with self.lock:
            super().__ior__(other)
            return self

    def __isub__(self, other: AbstractSet[object]) -> LockedSet[T]:
        with self.lock:
            super().__isub__(other)
            return self

    def __ixor__(self, other: AbstractSet[T]) -> LockedSet[T]:  # type: ignore[override,misc]
        with self.lock:
            super().__ixor__(other)
            return self

    def add(self, item: T) -> None:
        with self.lock:
            return super().add(item)

    def clear(self) -> None:
        with self.lock:
            return super().clear()

    def difference_update(self, *others: Iterable[object]) -> None:
        with self.lock:
            return super().difference_update(*others)

    def discard(self, item: object) -> None:
        with self.lock:
            return super().discard(item)

    def intersection_update(self, *others: Iterable[object]) -> None:
        with self.lock:
            return super().intersection_update(*others)

    def pop(self) -> T:
        with self.lock:
            return super().pop()

    def remove(self, item: T) -> None:
        with self.lock:
            return super().discard(item)

    def symmetric_difference_update(self, other: Iterable[T]) -> None:
        with self.lock:
            return super().symmetric_difference_update(other)

    def update(self, *others: Iterable[T]) -> None:
        with self.lock:
            return super().update(*others)
