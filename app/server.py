
from __future__ import annotations

from typing import List, Callable
from threading import Thread

from app.protocols.metaplace import MetaplaceWorldServer
from app.engine.matchmaking import MatchmakingQueue
from app.data import ServerType, BuildType
from app.engine.penguin import Penguin
from app.objects import Games

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
            stylesheet_id='87.5309',
            server_type=ServerType.LIVE,
            build_type=BuildType.RELEASE
        )

        self.matchmaking = MatchmakingQueue()
        self.games = Games()

        self.logger = logging.getLogger("Snowflake")
        self.threads: List[Thread] = []
        self.shutting_down = False

    def runThread(self, func: Callable, *args, **kwargs):
        thread = Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        self.threads.append(thread)

    def stopFactory(self):
        self.logger.warning("Shutting down...")
        self.shutting_down = True

        def force_exit(signal, frame):
            self.logger.warning("Force exiting...")
            os._exit(0)

        signal.signal(signal.SIGINT, force_exit)

        for thread in self.threads:
            thread.join()
