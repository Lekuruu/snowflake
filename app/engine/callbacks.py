
from __future__ import annotations

from typing import Callable, Dict, List, TYPE_CHECKING
from twisted.internet import reactor
from collections import defaultdict

if TYPE_CHECKING:
    from app.engine.game import Game

class CallbackHandler:
    def __init__(self, game: "Game"):
        self.pending_animations: Dict[int, List[int]] = defaultdict(list)
        self.callbacks: Dict[int, Callable] = {}
        self.game = game

    @property
    def pending_animation_ids(self) -> List[int]:
        return [id for ids in self.pending_animations.values() for id in ids]

    def register_animation(self, object_id: int, callback: Callable | None = None) -> int:
        id = self.next_id()

        if id not in self.pending_animations[object_id]:
            self.pending_animations[object_id].append(id)

        if callback is not None:
            self.callbacks[id] = callback

        return id

    def animation_done(self, id: int):
        for object_id, ids in self.pending_animations.items():
            if id not in ids:
                continue

            self.pending_animations[object_id].remove(id)
            break

        if id in self.callbacks:
            reactor.callInThread(self.callbacks[id], self.game.objects.by_id(object_id))
            self.callbacks.pop(id)

    def next_id(self) -> int:
        return max(self.pending_animation_ids, default=0) + 1
