
from __future__ import annotations

from threading import Lock, Thread
from typing import List, Callable

from app.engine.place import SnowLobby, SnowBattle, TuskBattle
from app.protocols.metaplace import MetaplaceWorldServer
from app.engine.matchmaking import MatchmakingQueue
from app.data import ServerType, BuildType
from app.engine.penguin import Penguin
from app.objects import Games

import app.session
import logging
import signal
import config
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
            policy_domain=config.POLICY_DOMAIN,
            policy_port=config.PORT,
            server_type=ServerType.LIVE,
            build_type=BuildType.RELEASE
        )

        self.matchmaking = MatchmakingQueue()
        self.games = Games()

        self.logger = logging.getLogger("Snowflake")
        self.threads: List[Thread] = []
        self.threads_lock = Lock()
        self.shutting_down = False

        self.sound_assets = app.session.sound_assets
        self.assets = app.session.assets

    def runThread(self, func: Callable, *args, **kwargs):
        def run():
            try:
                func(*args, **kwargs)
            finally:
                with self.threads_lock:
                    self.threads.remove(thread)

        thread = Thread(target=run)

        with self.threads_lock:
            self.threads.append(thread)
            thread.start()

    def startFactory(self):
        self.register_place(SnowLobby())
        self.register_place(SnowBattle())
        self.register_place(TuskBattle())

    def stopFactory(self):
        def force_exit(signal, frame):
            self.logger.warning("Force exiting...")
            os._exit(0)

        signal.signal(signal.SIGINT, force_exit)

        with self.threads_lock:
            threads = list(self.threads)

        for thread in threads:
            thread.join()
