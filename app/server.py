
from __future__ import annotations
from typing import List

from app.engine.place import SnowLobby, SnowBattle, TuskBattle
from app.protocols.metaplace import MetaplaceWorldServer
from app.engine.matchmaking import MatchmakingQueue
from app.data import ServerType, BuildType
from app.engine.penguin import Penguin
from app.objects import Games

import app.session
import asyncio
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
        self.tasks: List[asyncio.Task] = []
        self.shutting_down = False

        self.sound_assets = app.session.sound_assets
        self.assets = app.session.assets

    def startFactory(self):
        self.register_place(SnowLobby())
        self.register_place(SnowBattle())
        self.register_place(TuskBattle())

    def stopFactory(self):
        def force_exit(signal, frame):
            self.logger.warning("Force exiting...")
            os._exit(0)

        signal.signal(signal.SIGINT, force_exit)

        for task in list(self.tasks):
            task.cancel()

    def runCoroutine(self, coro) -> asyncio.Task:
        """Schedule a coroutine as a task on the reactor's asyncio event loop"""
        task = asyncio.get_running_loop().create_task(coro)
        self.tasks.append(task)
        task.add_done_callback(self.on_coroutine_done)
        return task

    def on_coroutine_done(self, task: asyncio.Task) -> None:
        if task in self.tasks:
            self.tasks.remove(task)

        if task.cancelled():
            return

        if (error := task.exception()) is not None:
            self.logger.error(f"Game routine failed: {error}", exc_info=error)
