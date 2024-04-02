
from twisted.internet.address import IPv4Address

from app.engine.penguin import Penguin
from app.data import penguins

class PenguinAI(Penguin):
    def __init__(
        self,
        server,
        element: str,
        battle_mode: int
    ) -> None:
        super().__init__(server, IPv4Address('TCP', '127.0.0.1', 69420))
        self.object = penguins.fetch_random()
        self.name = self.object.nickname
        self.element = element
        self.battle_mode = battle_mode
        self.pid = -1
        self.in_queue = True
        self.is_ready = True
        self.logged_in = True
        self.is_bot = True

    def select_move(self) -> None:
        # TODO: Implement move selection
        ...
