
from twisted.internet.address import IPv4Address, IPv6Address
from twisted.internet.protocol import Factory

from ..data import ServerType, BuildType
from .penguin import Penguin

import logging

class SnowflakeEngine(Factory):
    def __init__(self):
        self.players: set[Penguin] = set()
        self.protocol = Penguin

        self.server_type = ServerType.LIVE
        self.build_type = BuildType.RELEASE
        self.world_id = 101

        self.logger = logging.getLogger("snowflake")

    def buildProtocol(self, address: IPv4Address | IPv6Address):
        self.logger.info(f'-> "{address.host}:{address.port}"')
        self.players.add(player := self.protocol(self, address))
        return player
