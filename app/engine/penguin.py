
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from twisted.python.failure import Failure

if TYPE_CHECKING:
    from app.objects.ninjas import Ninja
    from .game import Game

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.internet.protocol import Factory

from app.data.objects import Penguin as PenguinObject
from app.data import BuildType, EventType, Phase
from .windows import WindowManager
from .receiver import Receiver

class Penguin(Receiver):
    def __init__(self, server: Factory, address: IPv4Address | IPv6Address):
        super().__init__(server, address)

        self.pid: int = 0
        self.name: str = ""
        self.token: str = ""
        self.logged_in: bool = False

        self.battle_mode: int = 0
        self.screen_size: str = ''
        self.asset_url: str = ''

        self.object: PenguinObject | None = None
        self.ninja: "Ninja" | None = None
        self.game: "Game" | None = None
        self.element: str = ""

        self.tip_mode: bool = True
        self.last_tip: Phase | None = None
        self.displayed_tips: List[Phase] = []

        self.disconnected: bool = False
        self.in_queue: bool = False
        self.is_ready: bool = False
        self.was_ko: bool = False
        self.loaded: bool = False

        self.window_manager = WindowManager(self)

    def __repr__(self) -> str:
        return f"<{self.name} ({self.pid})>"

    @property
    def is_member(self) -> bool:
        return True # TODO

    @property
    def in_game(self) -> bool:
        return self.game is not None

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

    def close_connection(self):
        if self.logged_in:
            self.send_to_room()
        return super().close_connection()

    def connectionLost(self, reason: Failure | None = None) -> None:
        super().connectionLost(reason)
        if self.in_game:
            self.ninja.set_health(0)

    def send_to_room(self) -> None:
        # This will load a window, that sends the player back to the room
        window = self.window_manager.get_window('cardjitsu_snowexternalinterfaceconnector.swf')
        window.layer = 'toolLayer'
        window.load(type=EventType.IMMEDIATE.value)

    def send_error(self, message: str) -> None:
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
        self.send_tag('P_MAPBLOCK', 't', 1, 1, 'iVBORw0KGgoAAAANSUhEUgAAAAkAAAAFCAAAAACyOJm3AAAADklEQVQImWNghgEGIlkADWEAiDEh28IAAAAASUVORK5CYII=')
        self.send_tag('P_MAPBLOCK', 'h', 1, 1, 'iVBORw0KGgoAAAANSUhEUgAAAAoAAAAGCAAAAADfm1AaAAAADklEQVQImWOohwMG8pgA1rMdxRJRFewAAAAASUVORK5CYII=')

        self.send_tag('UI_ALIGN', self.server.world_id, 0, 0, 'center', 'scale_none')
        self.send_tag('UI_BGCOLOR', 34, 164, 243)
        self.send_tag('W_PLACE', 0, 1, 0)

        self.send_tag('P_ZOOMLIMIT', -1.000000, -1.000000)
        self.send_tag('P_RENDERFLAGS', 0, 48)
        self.send_tag('P_SIZE', 9, 5)
        self.send_tag('P_VIEW', 5)
        self.send_tag('P_START', 5, 2.5, 0)
        self.send_tag('P_LOCKVIEW', 0)
        self.send_tag('P_TITLESIZE', 100)
        self.send_tag('P_ELEVSCALE', 0.031250)
        self.send_tag('P_RELIEF', 1)
        self.send_tag('P_LOCKSCROLL', 1, 0, 0, 0)
        self.send_tag('P_LOCKOBJECTS', 0)
        self.send_tag('P_HEIGHTMAPSCALE', 0.5, 0)
        self.send_tag('P_HEIGHTMAPDIVISION', 1)
        self.send_tag('P_DRAG', 0)
        self.send_tag('P_CAMLIMITS', 0, 0, 0, 0)
        self.send_tag('P_LOCKRENDERSIZE', 0, 1024, 768)
        self.send_tag('P_ASSETSCOMPLETE')

        # TODO: Find out what all of the tags do

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
