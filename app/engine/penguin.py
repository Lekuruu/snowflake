
from __future__ import annotations

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.internet.protocol import Factory

from .receiver import Receiver

class Penguin(Receiver):
    def __init__(self, server: Factory, address: IPv4Address | IPv6Address):
        super().__init__(server, address)

        self.pid: int = 0
        self.name: str = ""
        self.token: str = ""

    def __repr__(self) -> str:
        return f"<{self.name} ({self.pid})>"
