
from __future__ import annotations

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.protocols.basic import LineOnlyReceiver

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
