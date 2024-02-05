
from __future__ import annotations

from typing import Callable, Dict, List, TYPE_CHECKING
from twisted.internet import reactor
from collections import defaultdict
from dataclasses import dataclass
from enum import IntEnum

if TYPE_CHECKING:
    from app.engine.game import Game

class ActionType(IntEnum):
    Animation = 0
    Sound = 1

@dataclass
class Action:
    name: str
    handle_id: int
    object_id: int
    type: ActionType
    callback: Callable | None = None

    def __eq__(self, action: "Action") -> bool:
        return self.handle_id == action.handle_id

    def __hash__(self) -> int:
        return hash(self.handle_id)

class CallbackHandler:
    """This class manages callbacks for animations and sounds"""

    def __init__(self, game: "Game"):
        self.pending: Dict[int, List[Action]] = defaultdict(list)
        self.game = game

    @property
    def ids(self) -> List[int]:
        return [
            action.handle_id
            for actions in list(self.pending.values())
            for action in actions
        ]

    @property
    def actions(self) -> List[Action]:
        return [
            action
            for actions in list(self.pending.values())
            for action in actions
        ]

    @property
    def pending_animations(self) -> List[Action]:
        return [
            action
            for action in self.actions
            if action.type == ActionType.Animation
        ]

    @property
    def pending_sounds(self) -> List[Action]:
        return [
            action
            for action in self.actions
            if action.type == ActionType.Sound
        ]

    def by_id(self, id: int) -> Action | None:
        return next([action for action in self.actions if action.handle_id == id], None)

    def by_name(self, name: str) -> Action | None:
        return next([action for action in self.actions if action.name == name], None)

    def remove(self, object_id: int) -> None:
        if object_id in self.pending:
            self.pending.pop(object_id, None)

    def next_id(self) -> int:
        return max(self.ids or [0]) + 1

    def register_action(
        self,
        name: str,
        type: ActionType,
        object_id: int,
        callback: Callable | None = None
    ) -> int:
        action = Action(
            name,
            self.next_id(),
            object_id,
            type,
            callback
        )

        self.pending[object_id].append(action)
        return action.handle_id

    def action_done(self, id: int, object_id: int):
        target_object = self.game.objects.by_id(object_id)

        for action in self.pending[object_id]:
            if action.handle_id != id:
                continue

            if action.callback is not None:
                reactor.callInThread(
                    action.callback,
                    target_object
                )

            self.pending[object_id].remove(action)
            break
