
from __future__ import annotations
from typing import Any, List

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.internet.protocol import Factory

from ..data import BuildType, MessageType, EventType
from .windows import WindowManager, SWFWindow
from .receiver import Receiver

import json

class Penguin(Receiver):
    def __init__(self, server: Factory, address: IPv4Address | IPv6Address):
        super().__init__(server, address)

        self.pid: int = 0
        self.name: str = ""
        self.token: str = ""
        self.logged_in: bool = False

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

    def load_assets(self) -> None:
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
