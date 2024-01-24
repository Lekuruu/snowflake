
from __future__ import annotations

from typing import Any, List

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.internet.protocol import Factory

from ..data.objects import Penguin as PenguinObject
from ..data import BuildType, EventType
from .windows import WindowManager
from .receiver import Receiver
from .game import Game

import json

class Penguin(Receiver):
    def __init__(self, server: Factory, address: IPv4Address | IPv6Address):
        super().__init__(server, address)

        self.pid: int = 0
        self.name: str = ""
        self.token: str = ""
        self.logged_in: bool = False

        self.object: PenguinObject | None = None
        self.game: Game | None = None

        self.element: str = ""
        self.tip_mode: bool = True

        self.hp: int = 0
        self.range: int = 0
        self.power: int = 0
        self.move: int = 0

        self.in_queue: bool = False
        self.in_game: bool = False
        self.is_host: bool = False

        self.window_manager = WindowManager(self)

    def __repr__(self) -> str:
        return f"<{self.name} ({self.pid})>"

    def command_received(self, command: str, args: List[Any]):
        try:
            self.server.events.call(
                self,
                command,
                args
            )
        except Exception as e:
            self.logger.error(f'Failed to execute event: {e}', exc_info=e)
            self.close_connection()
            return

    def send_to_room(self) -> None:
        # This will load a window, that sends the player back to the room
        window = self.window_manager.get_window('cardjitsu_snowexternalinterfaceconnector.swf')
        window.layer = 'toolLayer'
        window.load(type=EventType.IMMEDIATE.value)

    def send_error(self, message: str) -> None:
        # This will load a window, that sends the player back to the room
        window = self.window_manager.get_window('cardjitsu_snowerrorhandler.swf')
        window.send_payload(
            'error',
            {
                'msg': message,
                'code': 0, # TODO
                'data': '' # TODO
            }
        )

    def initialize_game(self) -> None:
        self.send_tag('UI_BGCOLOR', 34, 164, 243)
        # TODO: Load assets
        self.send_tag('P_ASSETSCOMPLETE')

    def send_login_reply(self):
        self.send_tag(
            'S_LOGIN',
            self.pid
        )

    def send_login_message(self, message: str):
        self.send_tag(
            'S_LOGINDEBUG',
            message
        )

    def send_login_error(self, code: int = 900):
        self.send_tag(
            'S_LOGINDEBUG',
            f'user code {code}'
        )

    def send_world_type(self):
        self.send_tag(
            'S_WORLDTYPE',
            self.server.server_type.value,
            self.server.build_type.value
        )

    def send_world(self):
        self.send_tag(
            'S_WORLD',
            self.server.world_id,                                  # World ID
            self.server.world_name,                                # World Name
            '0:113140001',                                         # start_placeUniqueId ???
            1 if self.server.build_type == BuildType.DEBUG else 0, # devMode
            'none',                                                # ?
            0,                                                     # ?
            'crowdcontrol',                                        # ?
            self.server.world_name,                                # clean_name
            0,                                                     # ?
            '200.5991',                                            # STYLESHEET_ID ?
            0                                                      # ?
        )
