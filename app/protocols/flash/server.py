
from __future__ import annotations

from app.protocols.flash import SocketPolicyHandler
from twisted.internet.address import IPv4Address, IPv6Address
from twisted.internet.protocol import Factory
from twisted.internet import reactor

import logging

class SocketPolicyServer(Factory):
    protocol = SocketPolicyHandler

    def __init__(self):
        self.logger = logging.getLogger("SocketPolicyServer")
        self.policy = (
            "<cross-domain-policy>"
            "<allow-access-from domain='*' to-ports='*' />"
            "</cross-domain-policy>"
        )

    def buildProtocol(self, address: IPv4Address | IPv6Address):
        self.logger.debug(f"-> {address.host}:{address.port}")
        return self.protocol(address, self.policy)

    def listen(self, port: int):
        self.logger.info(f"Starting engine: {self} ({port})")
        reactor.listenTCP(port, self)
