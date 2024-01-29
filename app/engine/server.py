
from __future__ import annotations

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.internet.protocol import Factory
from twisted.internet import reactor

from app.events import EventHandler, FunnelHandler, TriggerHandler
from app.data import ServerType, BuildType, Postgres
from app.objects import Players, AssetCollection

from .matchmaking import MatchmakingQueue
from .penguin import Penguin

import logging
import signal
import config
import os

class SnowflakeEngine(Factory):
    def __init__(self):
        self.players = Players()
        self.protocol = Penguin
        self.shutting_down = False

        self.server_type = ServerType.LIVE
        self.build_type = BuildType.RELEASE

        self.world_id = 101
        self.world_name = "clubpenguin_town_en_3"

        self.logger = logging.getLogger("snowflake")

        self.events = EventHandler()
        self.actions = FunnelHandler()
        self.triggers = TriggerHandler()
        self.matchmaking = MatchmakingQueue()

        self.assets = AssetCollection()
        self.sound_assets = AssetCollection()

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
        self.shutting_down = True

        def force_exit(signal, frame):
            logging.warning("Force exiting...")
            os._exit(0)

        signal.signal(signal.SIGINT, force_exit)

    def run(self):
        self.logger.info(f"Starting engine: {self} ({config.PORT})")
        reactor.listenTCP(config.PORT, self)
        reactor.run()

Instance = SnowflakeEngine()
