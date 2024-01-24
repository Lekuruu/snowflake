
from twisted.internet.address import IPv4Address, IPv6Address
from twisted.internet.protocol import Factory
from twisted.internet import reactor

from ..events import EventHandler, ActionHandler, TriggerHandler
from ..objects.collections import AssetCollection, Players
from ..data import ServerType, BuildType, Postgres
from .matchmaking import MatchmakingQueue
from .penguin import Penguin

import logging
import config

class SnowflakeEngine(Factory):
    def __init__(self):
        self.players = Players()
        self.protocol = Penguin

        self.server_type = ServerType.LIVE
        self.build_type = BuildType.RELEASE

        self.world_id = 101
        self.world_name = "clubpenguin_town_en_3"

        self.logger = logging.getLogger("snowflake")

        self.events = EventHandler()
        self.actions = ActionHandler()
        self.assets = AssetCollection()
        self.triggers = TriggerHandler()
        self.matchmaking = MatchmakingQueue()

        self.database = Postgres(
            config.POSTGRES_USER,
            config.POSTGRES_PASSWORD,
            config.POSTGRES_HOST,
            config.POSTGRES_PORT
        )

    def buildProtocol(self, address: IPv4Address | IPv6Address):
        self.logger.info(f'-> "{address.host}:{address.port}"')
        self.players.add(player := self.protocol(self, address))
        return player

    def stopFactory(self):
        self.logger.warning("Shutting down...")

    def run(self):
        self.logger.info(f"Starting engine: {self} ({config.PORT})")
        reactor.listenTCP(config.PORT, self)
        reactor.run()

Instance = SnowflakeEngine()
