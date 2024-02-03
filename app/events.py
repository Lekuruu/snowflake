
from typing import Callable, Dict, List, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from app.engine import Penguin

class EventHandler:
    def __init__(self) -> None:
        self.handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger("Events")

    def call(self, client: "Penguin", type: str, args: List[str]) -> None:
        if type != '/framework':
            self.logger.debug(f'{type}: {args}')

        if type in self.handlers:
            self.handlers[type](client, *args)
            return

        self.logger.warning(f'Unknown event: "{type}"')

    def register(self, type: str, login_required: bool = True) -> Callable:
        def wrapper(handler: Callable) -> Callable:
            def login_wrapper(client: "Penguin", *args):
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

class FrameworkHandler:
    def __init__(self) -> None:
        self.handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger("Framework")

    def call(self, trigger: str, client: "Penguin", data: dict) -> None:
        if not client.window_manager.loaded:
            return

        self.logger.debug(f"{trigger}: {data}")

        if trigger in self.handlers:
            self.handlers[trigger](client, data)
            return

        self.logger.warning(f'Unknown event: "{trigger}"')

    def register(self, trigger: str):
        def wrapper(handler: Callable):
            self.handlers[trigger] = handler
            self.logger.info(f"Registered trigger: {trigger}")
            return handler
        return wrapper
