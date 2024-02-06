
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from app.objects.ninjas import Ninja
    from app.engine.game import Game

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.internet.protocol import Factory
from twisted.python.failure import Failure

from app.protocols import MetaplaceProtocol
from app.data import (
    Penguin as PenguinObject,
    MapblockType,
    AlignMode,
    ScaleMode,
    EventType,
    ViewMode,
    Phase,
    Card
)

import app.session

class Penguin(MetaplaceProtocol):
    def __init__(self, server: Factory, address: IPv4Address | IPv6Address):
        super().__init__(server, address)

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
        self.power_cards: List[Card] = []

        self.in_queue: bool = False
        self.is_ready: bool = False
        self.was_ko: bool = False

    def __repr__(self) -> str:
        return f"<{self.name} ({self.pid})>"

    @property
    def is_member(self) -> bool:
        return True # TODO

    @property
    def in_game(self) -> bool:
        return self.game is not None

    @property
    def power_cards_water(self) -> List[Card]:
        return [c for c in self.power_cards if c.element == 'w']

    @property
    def power_cards_fire(self) -> List[Card]:
        return [c for c in self.power_cards if c.element == 'f']

    @property
    def power_cards_snow(self) -> List[Card]:
        return [c for c in self.power_cards if c.element == 's']

    def command_received(self, command: str, args: List[Any]):
        try:
            app.session.events.call(
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

        # Put client in ready state, so that the game doesn't softlock
        self.is_ready = True

        return super().close_connection()

    def connectionLost(self, reason: Failure | None = None) -> None:
        if self.in_game and self.ninja:
            self.ninja.set_health(0)

        if reason is not None and not self.disconnected:
            self.logger.warning(f"Connection lost: {reason.getErrorMessage()}")

        self.server.matchmaking.remove(self)
        self.server.players.remove(self)
        self.disconnected = True

    def send_to_room(self) -> None:
        # This will load a window, that sends the player back to the room
        window = self.get_window('cardjitsu_snowexternalinterfaceconnector.swf')
        window.layer = 'toolLayer'
        window.load(type=EventType.IMMEDIATE.value)

    def send_error(self, message: str) -> None:
        window = self.get_window('cardjitsu_snowerrorhandler.swf')
        window.send_payload(
            'error',
            {
                'msg': message,
                'code': 0, # TODO
                'data': '' # TODO
            }
        )

    def send_tip(self, phase: Phase) -> None:
        infotip = self.get_window('cardjitsu_snowinfotip.swf')
        infotip.layer = 'topLayer'
        infotip.load(
            {
                'element': self.element,
                'phase': phase.value,
            },
            loadDescription="",
            assetPath="",
            xPercent=0.1,
            yPercent=0
        )
        self.last_tip = phase

        def on_close(client: "Penguin"):
            client.last_tip = None

        infotip.on_close = on_close

    def hide_tip(self) -> None:
        infotip = self.get_window('cardjitsu_snowinfotip.swf')
        infotip.send_payload('disable')

    def initialize_game(self) -> None:
        self.align_ui(0, 0, AlignMode.CENTER, ScaleMode.NONE)
        self.set_background_color(34, 164, 243)
        self.set_place(0, 1, 0)

        self.set_mapblock(MapblockType.TILEMAP, 'iVBORw0KGgoAAAANSUhEUgAAAAkAAAAFCAAAAACyOJm3AAAADklEQVQImWNghgEGIlkADWEAiDEh28IAAAAASUVORK5CYII=')
        self.set_mapblock(MapblockType.HEIGHTMAP, 'iVBORw0KGgoAAAANSUhEUgAAAAoAAAAGCAAAAADfm1AaAAAADklEQVQImWOohwMG8pgA1rMdxRJRFewAAAAASUVORK5CYII=')
        self.set_heighmap_division(1)

        self.set_view_mode(ViewMode.VIEW_MODE_SIDE)
        self.set_tilesize(100)

        self.set_renderflags(False, 48)
        self.lock_rendersize(1024, 768)
        self.send_tag('P_ASSETSCOMPLETE')
