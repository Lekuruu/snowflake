
from __future__ import annotations

from typing import Callable, Dict, List, Any, TYPE_CHECKING
from twisted.internet import reactor
from collections import defaultdict
from dataclasses import dataclass
from enum import IntEnum

import time

if TYPE_CHECKING:
    from app.engine.game import Game
    from app.engine import Penguin

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
    """This class manages callbacks for animations, sounds & window events"""

    def __init__(self, game: "Game"):
        self.pending_actions: Dict[int, List[Action]] = defaultdict(list)
        self.pending_events: Dict[Any, List[str]] = defaultdict(list)
        self.game = game

    @property
    def ids(self) -> List[int]:
        return [
            action.handle_id
            for actions in list(self.pending_actions.values())
            for action in actions
        ]

    @property
    def actions(self) -> List[Action]:
        return [
            action
            for actions in list(self.pending_actions.values())
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
        if object_id in self.pending_actions:
            self.pending_actions.pop(object_id, None)

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

        self.pending_actions[object_id].append(action)
        return action.handle_id

    def action_done(self, id: int, object_id: int):
        target_object = self.game.objects.by_id(object_id)

        for action in self.pending_actions[object_id]:
            if action.handle_id != id:
                continue

            if action.callback is not None:
                reactor.callInThread(
                    action.callback,
                    target_object
                )

            self.pending_actions[object_id].remove(action)
            break

    def register_event(self, target: Any, event: str) -> None:
        self.pending_events[target].append(event)

    def event_done(self, event: str, target: Any) -> None:
        if event in self.pending_events.get(target, []):
            self.pending_events[target].remove(event)

    def remove_events(self, target: Any) -> None:
        if target in self.pending_events:
            self.pending_events.pop(target, None)

    def wait_for_client(self, event: str, client: "Penguin", timeout=8) -> None:
        """Wait for an event to be called by the client"""
        self.register_event(client, event)

        start_time = time.time()

        while event in self.pending_events.get(client, []):
            if client.disconnected:
                self.remove_events(client)
                break

            if client.is_bot:
                self.remove_events(client)
                break

            if time.time() - start_time > timeout:
                self.game.logger.warning(f"Event Timeout: {event}")
                self.remove_events(client)
                break

            time.sleep(0.05)

    def wait_for_event(self, event: str, timeout=8) -> None:
        """Wait for an event to be called by any of the clients"""
        self.register_event(self.game, event)

        start_time = time.time()

        while event in self.pending_events.get(self.game, []):
            if time.time() - start_time > timeout:
                self.game.logger.warning(f"Event Timeout: {event}")
                self.reset_events()
                break

            time.sleep(0.05)

    def reset_animations(self) -> None:
        self.pending_actions.clear()

    def reset_events(self) -> None:
        self.pending_events.clear()
