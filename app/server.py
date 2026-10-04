
from __future__ import annotations

from app.engine.place import SnowLobby, SnowBattle, TuskBattle
from app.protocols.metaplace import MetaplaceWorldServer
from app.engine.matchmaking import MatchmakingQueue
from app.data import BuildType, DataProvider, ServerType
from app.data import load_data_provider
from app.engine.penguin import Penguin
from app.objects import Games

import app.session
import app.handlers
import app.data.assets
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
        self.shutting_down = False

        self.sound_assets = app.session.sound_assets
        self.assets = app.session.assets
        self.data: DataProvider = load_data_provider(config.DATA_PROVIDER)

    def startFactory(self):
        self.register_place(SnowLobby())
        self.register_place(SnowBattle())
        self.register_place(TuskBattle())

    def stopFactory(self):
        def force_exit(signal, frame):
            self.logger.warning("Force exiting...")
            os._exit(0)

        signal.signal(signal.SIGINT, force_exit)
