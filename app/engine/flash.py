
from __future__ import annotations

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import Factory

import logging

# Read more about policy servers here:
#    https://clients.sisrv.net/knowledgebase/80/How-to-setup-Flash-Socket-Policy-File.html
#    http://www.adobe.com/devnet/flashplayer/articles/socket_policy_files.html

class SocketPolicyHandler(LineOnlyReceiver):

    delimiter = b'\x00'

    def __init__(self, address: IPv4Address | IPv6Address, policy: str):
        self.address = address
        self.policy = policy
        self.logger = logging.getLogger(address.host)

    def lineReceived(self, line: bytes):
        if line.startswith(b'<policy-file-request/>'):
            self.logger.debug(f'-> "{line}"')
            self.sendLine(self.policy.encode())
            self.closeConnection()

    def sendLine(self, line):
        self.logger.debug(f'<- "{line}"')
        return super().sendLine(line)

    def connectionLost(self, reason) -> None:
        self.logger.debug(f"-> Connection done")

    def closeConnection(self):
        self.transport.loseConnection()

class SocketPolicyServer(Factory):
    def __init__(self):
        self.logger = logging.getLogger("SocketPolicyServer")
        self.policy = (
            "<cross-domain-policy>"
            "<allow-access-from domain='*' to-ports='*' />"
            "</cross-domain-policy>"
        )

    def startFactory(self):
        self.logger.info(f"Starting engine: {self} (843)")

    def buildProtocol(self, address: IPv4Address | IPv6Address):
        self.logger.debug(f"-> {address.host}:{address.port}")
        return SocketPolicyHandler(address, self.policy)
