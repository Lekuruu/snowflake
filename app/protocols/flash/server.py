
from __future__ import annotations

from app.protocols.flash import SocketPolicyHandler
from twisted.internet.address import IPv4Address, IPv6Address
from twisted.internet.protocol import Factory
from twisted.internet import reactor

import logging

class SocketPolicyServer(Factory):
    protocol = SocketPolicyHandler

    def __init__(self, policy_domain: str = "*", policy_port: str = "*"):
        self.logger = logging.getLogger("SocketPolicyServer")
        self.policy = (
            f"<cross-domain-policy>"
            f"<allow-access-from domain='{policy_domain}' to-ports='{policy_port}' />"
            f"</cross-domain-policy>"
        )

    def buildProtocol(self, address: IPv4Address | IPv6Address):
        self.logger.debug(f"-> {address.host}:{address.port}")
        return self.protocol(address, self.policy)

    def listen(self, port: int):
        self.logger.info(f"Starting policy server ({port})")
        reactor.listenTCP(port, self)
