
from __future__ import annotations

from typing import List, Callable
from threading import Thread

from app.protocols.metaplace import MetaplaceWorldServer
from app.engine.matchmaking import MatchmakingQueue
from app.engine.place import SnowLobby, SnowBattle
from app.data import ServerType, BuildType
from app.engine.penguin import Penguin
from app.objects import Games

import app.session
import logging
import signal
import os

class SnowflakeWorld(MetaplaceWorldServer):
    protocol = Penguin

    def __init__(self):
        # TODO: Make this configurable
        super().__init__(
            world_id=101,
            world_name='cjsnow_0',
            world_owner='crowdcontrol',
            stylesheet_id='87.5309',
            server_type=ServerType.LIVE,
            build_type=BuildType.RELEASE
        )

        self.matchmaking = MatchmakingQueue()
        self.games = Games()

        self.logger = logging.getLogger("Snowflake")
        self.threads: List[Thread] = []
        self.shutting_down = False

        self.sound_assets = app.session.sound_assets
        self.assets = app.session.assets

    def runThread(self, func: Callable, *args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        self.threads.append(thread)

    def startFactory(self):
        self.register_place(SnowLobby())
        self.register_place(SnowBattle())

    def stopFactory(self):
        self.logger.warning("Shutting down...")
        self.shutting_down = True

        def force_exit(signal, frame):
            self.logger.warning("Force exiting...")
            os._exit(0)

        signal.signal(signal.SIGINT, force_exit)

        for thread in self.threads:
            thread.join()
