
from typing import Callable, Dict
import logging

class EventHandler:
    def __init__(self) -> None:
        self.handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger("events")

    def call(self, client, type, args) -> None:
        self.logger.debug(f'Called "{type}": {args}')
        if type in self.handlers:
            for handler in self.handlers[type]:
                handler(client, *args)

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
