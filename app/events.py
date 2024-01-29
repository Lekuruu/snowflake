
from typing import Callable, Dict, List, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from app.engine import Penguin

class EventHandler:
    def __init__(self) -> None:
        self.handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger("events")

    def call(self, client: "Penguin", type: str, args: List[str]) -> None:
        if type in self.handlers:
            self.handlers[type](client, *args)
            return

        self.logger.warning(f'Unknown event: "{type}"')

    def register(self, type: str, login_required: bool = True) -> Callable:
        def wrapper(handler: Callable) -> Callable:
            def login_wrapper(client, *args):
                if not client.logged_in: return
                handler(client, *args)

            if login_required:
                # Add wrapper function that checks for login
                self.handlers[type] = login_wrapper
            else:
                self.handlers[type] = handler

            self.logger.info(f'Registered event: "{type}"')
            return self.handlers[type]
        return wrapper

class TriggerHandler(EventHandler):
    def __init__(self) -> None:
        self.handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger("triggers")

    def call(self, trigger: str, client: "Penguin", json: dict) -> None:
        if not client.window_manager.loaded:
            return
        return super().call(client, trigger, [json])

    def register(self, trigger: str):
        def wrapper(handler: Callable):
            self.handlers[trigger] = handler
            self.logger.info(f"Registered trigger: {trigger}")
            return handler
        return wrapper

class FunnelHandler:
    def __init__(self) -> None:
        self.logger = logging.getLogger("funnel")

    def call(self, action: str, client: "Penguin", json: dict) -> None:
        # TODO: Add datadog logging for funnel analysis
        self.logger.debug(f"{action}: {json}")
