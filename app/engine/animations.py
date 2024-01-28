
from __future__ import annotations

from typing import Callable, Dict, List, TYPE_CHECKING
from twisted.internet import reactor

if TYPE_CHECKING:
    from app.engine.game import Game

class AnimationCallbacks:
    def __init__(self, game: "Game"):
        self.callbacks: Dict[int, Callable] = {}
        self.pending: List[int] = []
        self.game = game

    def register(self, callback: Callable | None = None) -> int:
        id = self.next_id()

        if id not in self.pending:
            self.pending.append(id)

        if callback is not None:
            self.callbacks[id] = callback

        return id

    def animation_done(self, id: int):
        if id in self.pending:
            self.pending.remove(id)

        if id in self.callbacks:
            reactor.deferToThread(self.callbacks[id], self.game)

    def next_id(self) -> int:
        return max(self.pending or [0]) + 1
