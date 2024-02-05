
from __future__ import annotations

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.internet.protocol import Factory
from typing import List, Callable
from threading import Thread
from redis import Redis

from app.objects import Players, AssetCollection, Games
from app.data import ServerType, BuildType, Postgres
from app.events import EventHandler, FrameworkHandler

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
        self.world_name = "cjsnow_0"

        self.logger = logging.getLogger("Snowflake")

        self.games = Games()
        self.events = EventHandler()
        self.triggers = FrameworkHandler()
        self.matchmaking = MatchmakingQueue()

        self.assets = AssetCollection()
        self.sound_assets = AssetCollection()

        self.database = Postgres(
            config.POSTGRES_USER,
            config.POSTGRES_PASSWORD,
            config.POSTGRES_HOST,
            config.POSTGRES_PORT
        )

        self.redis = Redis(
            config.REDIS_HOST,
            config.REDIS_PORT,
            config.REDIS_DB,
            config.REDIS_PASSWORD
        )

        self.threads: List[Thread] = []

    def runThread(self, func: Callable, *args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        self.threads.append(thread)

    def buildProtocol(self, address: IPv4Address | IPv6Address):
        self.logger.debug(f'-> "{address.host}:{address.port}"')
        self.players.add(player := self.protocol(self, address))
        return player

    def startFactory(self):
        self.logger.info(f"Starting engine: {self} ({config.PORT})")

    def stopFactory(self):
        self.logger.warning("Shutting down...")
        self.shutting_down = True

        def force_exit(signal, frame):
            self.logger.warning("Force exiting...")
            os._exit(0)

        signal.signal(signal.SIGINT, force_exit)

        for thread in self.threads:
            thread.join()

Instance = SnowflakeEngine()
