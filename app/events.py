
from typing import Callable, Dict, List
from app.engine import Penguin

import logging

class EventHandler:
    def __init__(self) -> None:
        self.handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger("events")

    def call(self, client: "Penguin", type: str, args: List[str]) -> None:
        self.logger.debug(f'Called "{type}": {args}')

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
                handler = login_wrapper

            self.handlers[type] = handler
            self.logger.info(f'Registered event: "{type}"')
            return handler
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

class ActionHandler(EventHandler):
    def __init__(self) -> None:
        self.handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger("actions")

    def call(self, action: str, client: "Penguin", json: dict) -> None:
        if not client.window_manager.loaded:
            return
        return super().call(client, action, [json])

    def register(self, action: str):
        def wrapper(handler: Callable):
            self.handlers[action] = handler
            self.logger.info(f"Registered action: {action}")
            return handler
        return wrapper
