
from typing import Callable, Dict, List
from collections import defaultdict
import logging

class EventHandler:
    def __init__(self) -> None:
        self.handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.logger = logging.getLogger("events")

    def call(self, client, type, args) -> None:
        self.logger.debug(f'Called "{type}": {args}')
        if type in self.handlers:
            for handler in self.handlers[type]:
                handler(client, *args)

    def delete(self, type):
        self.logger.debug(f'Deleting "{type}"...')
        if type in self.handlers:
            try:
                del self.handlers[type]
            except Exception as e:
                self.logger.error(f'Failed to delete "{type}": {e}')

    def register(self, type: str) -> Callable:
        def wrapper(handler: Callable) -> Callable:
            if type in self.handlers:
                self.handlers[type].append(handler)
            self.logger.info(f"Registered event: {type}")
            return handler
        return wrapper
