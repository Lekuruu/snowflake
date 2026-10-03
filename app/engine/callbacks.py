
from __future__ import annotations

from typing import Callable, Dict, List, Any, TYPE_CHECKING
from twisted.internet.defer import CancelledError, Deferred, TimeoutError
from twisted.internet import reactor
from dataclasses import dataclass
from enum import IntEnum

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

    def __hash__(self) -> int:
        return hash(self.handle_id)

    def __eq__(self, action: object) -> bool:
        if not isinstance(action, Action):
            return False
        return self.handle_id == action.handle_id

class CallbackHandler:
    """This class manages callbacks for animations, sounds & window events"""

    def __init__(self, game: "Game"):
        self.pending_actions: Dict[int, List[Action]] = {}
        self.pending_events: Dict[Any, Dict[str, List[Deferred]]] = {}
        self.animation_waiters: List[Deferred] = []
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
        return next((action for action in self.actions if action.handle_id == id), None)

    def by_name(self, name: str) -> Action | None:
        return next((action for action in self.actions if action.name == name), None)

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

        self.pending_actions.setdefault(object_id, []).append(action)
        return action.handle_id

    def action_done(self, id: int, object_id: int) -> None:
        actions = self.pending_actions.get(object_id)

        if not actions:
            return

        action = next(
            (action for action in actions if action.handle_id == id),
            None
        )

        if action is None:
            return

        actions.remove(action)

        if not actions:
            self.pending_actions.pop(object_id, None)

        if action.callback is not None:
            action.callback(self.game.objects.by_id(object_id))

        if not self.pending_animations:
            self.finish_waiters(self.animation_waiters, True)

    def register_event(self, target: Any, event: str) -> Deferred:
        waiter = Deferred()
        events = self.pending_events.setdefault(target, {})
        events.setdefault(event, []).append(waiter)
        return waiter

    def event_done(self, event: str, target: Any) -> None:
        events = self.pending_events.get(target, {})
        waiters = events.pop(event, [])

        if not waiters:
            return

        if not events:
            self.pending_events.pop(target, None)

        self.finish_waiters(waiters, event)

    def remove_events(self, target: Any) -> None:
        events = self.pending_events.pop(target, {})

        for waiters in events.values():
            self.cancel_waiters(waiters)

    async def wait_for_client(
        self,
        event: str,
        client: "Penguin",
        timeout: float = 8,
        waiter: Deferred | None = None
    ) -> bool:
        """Wait for an event to be called by the client"""
        waiter = waiter or self.register_event(client, event)
        return await self.await_event(waiter, client, event, timeout)

    async def wait_for_event(
        self,
        event: str,
        timeout: float = 8,
        waiter: Deferred | None = None
    ) -> bool:
        """Wait for an event to be called by any of the clients"""
        waiter = waiter or self.register_event(self.game, event)
        return await self.await_event(waiter, self.game, event, timeout)

    async def wait_for_animations(self, timeout: float = 8) -> bool:
        if not self.pending_animations:
            return True

        waiter = Deferred()
        self.animation_waiters.append(waiter)

        try:
            await waiter.addTimeout(timeout, reactor)
            return True
        except TimeoutError:
            self.game.logger.warning(f'Animation Timeout: {self.pending_animations}')
            self.reset_animations()
        except CancelledError:
            pass
        finally:
            if waiter in self.animation_waiters:
                self.animation_waiters.remove(waiter)

        return False

    def reset_animations(self) -> None:
        self.pending_actions.clear()
        self.finish_waiters(self.animation_waiters, False)

    def reset_events(self) -> None:
        for target in list(self.pending_events):
            self.remove_events(target)

    async def await_event(
        self,
        waiter: Deferred,
        target: Any,
        event: str,
        timeout: float
    ) -> bool:
        try:
            await waiter.addTimeout(timeout, reactor)
            return True
        except TimeoutError:
            self.game.logger.warning(f'Event Timeout: {event}')
        except CancelledError:
            pass
        finally:
            self.remove_event_waiter(target, event, waiter)

        return False

    def remove_event_waiter(
        self,
        target: Any,
        event: str,
        waiter: Deferred
    ) -> None:
        events = self.pending_events.get(target)
        if not events:
            return

        waiters = events.get(event)
        if waiters and waiter in waiters:
            waiters.remove(waiter)

        if waiters == []:
            events.pop(event, None)
        if not events:
            self.pending_events.pop(target, None)

    @staticmethod
    def finish_waiters(waiters: List[Deferred], result: Any) -> None:
        pending = list(waiters)
        waiters.clear()

        for waiter in pending:
            if not waiter.called:
                waiter.callback(result)

    @staticmethod
    def cancel_waiters(waiters: List[Deferred]) -> None:
        pending = list(waiters)
        waiters.clear()

        for waiter in pending:
            if not waiter.called:
                waiter.cancel()
