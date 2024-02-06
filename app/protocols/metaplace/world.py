
from __future__ import annotations

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.internet.protocol import Factory
from twisted.internet import reactor

from app.protocols.metaplace import MetaplaceProtocol
from app.data import ServerType, BuildType
from app.objects import Players

import logging

class MetaplaceWorldServer(Factory):
    protocol = MetaplaceProtocol

    def __init__(
        self,
        world_id: int,
        world_name: str,
        stylesheet_id: str,
        server_type: ServerType = ServerType.LIVE,
        build_type: BuildType = BuildType.RELEASE
    ) -> None:
        self.world_id = world_id
        self.world_name = world_name
        self.build_type = build_type
        self.server_type = server_type
        self.stylesheet_id = stylesheet_id

        self.players = Players()
        self.logger = logging.getLogger(f"{world_name} ({world_id})")

        self.policy_file = (
            "<cross-domain-policy>"
            "<allow-access-from domain='*' to-ports='*' />"
            "</cross-domain-policy>"
        )

    def buildProtocol(self, address: IPv4Address | IPv6Address):
        self.logger.debug(f'-> "{address.host}:{address.port}"')
        self.players.add(player := self.protocol(self, address))
        return player

    def listen(self, port: int):
        self.logger.info(f"Starting engine: {self} ({port})")
        reactor.listenTCP(port, self)
