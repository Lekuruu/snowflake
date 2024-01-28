
from __future__ import annotations

from typing import Callable, Dict, List, TYPE_CHECKING
from twisted.internet import reactor

if TYPE_CHECKING:
    from app.engine.game import Game

class CallbackHandler:
    def __init__(self, game: "Game"):
        self.callbacks: Dict[int, Callable] = {}
        self.pending_animations: List[int] = []
        self.pending_sounds: List[int] = []
        self.game = game

    def register_animation(self, callback: Callable | None = None) -> int:
        id = self.next_id()

        if id not in self.pending_animations:
            self.pending_animations.append(id)

        if callback is not None:
            self.callbacks[id] = callback

        return id

    def register_sound(self, callback: Callable | None = None) -> int:
        id = self.next_id()

        if id not in self.pending_sounds:
            self.pending_sounds.append(id)

        if callback is not None:
            self.callbacks[id] = callback

        return id

    def animation_done(self, id: int):
        if id in self.pending_animations:
            self.pending_animations.remove(id)

        if id in self.callbacks:
            reactor.deferToThread(self.callbacks[id], self.game)
            self.callbacks.pop(id)

    def sound_done(self, id: int):
        if id in self.pending_sounds:
            self.pending_sounds.remove(id)

        if id in self.callbacks:
            reactor.deferToThread(self.callbacks[id], self.game)
            self.callbacks.pop(id)

    def next_id(self) -> int:
        return max(self.pending_animations + self.pending_sounds, default=0) + 1
