
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from app.server import SnowflakeWorld
    from app.objects.ninjas import Ninja
    from app.engine.game import Game

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.python.failure import Failure

from app.protocols import MetaplaceProtocol
from app.engine.cards import CardObject
from app.data import (
    Penguin as PenguinObject,
    EventType,
    TipPhase,
    Card
)

import app.session
import random

class Penguin(MetaplaceProtocol):
    def __init__(self, server: "SnowflakeWorld", address: IPv4Address | IPv6Address):
        super().__init__(server, address)

        self.battle_mode: int = 0
        self.screen_size: str = ''
        self.asset_url: str = ''

        self.object: PenguinObject | None = None
        self.ninja: "Ninja" | None = None
        self.game: "Game" | None = None
        self.element: str = ""

        self.tip_mode: bool = True
        self.last_tip: TipPhase | None = None
        self.displayed_tips: List[TipPhase] = []

        self.selected_card: CardObject | None = None
        self.power_card_slots: List[CardObject] = []
        self.power_card_stamina: int = 0
        self.power_cards_all: List[Card] = []

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
        return [c for c in self.power_cards_all if c.element == 'w']

    @property
    def power_cards_fire(self) -> List[Card]:
        return [c for c in self.power_cards_all if c.element == 'f']

    @property
    def power_cards_snow(self) -> List[Card]:
        return [c for c in self.power_cards_all if c.element == 's']

    @property
    def power_cards(self) -> List[Card]:
        return [
            c for c in self.power_cards_all
            if c not in self.power_card_slots
            and c.element == self.element[0]
        ]

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

    def get_next_power_card(self) -> CardObject | None:
        if not self.power_cards:
            return

        if len(self.power_card_slots) > 3:
            return

        next_card = CardObject(random.choice(self.power_cards), self.game)
        self.power_card_slots.append(next_card)
        return next_card

    def get_power_card(self, card_id: int) -> Card | None:
        return next((c for c in self.power_card_slots if c.id == card_id), None)

    def update_cards(self) -> None:
        if self.disconnected:
            return

        self.power_card_stamina += 1

        update = {
            'cardData': None,
            'cycle': False,
            'stamina': self.power_card_stamina
        }

        if self.power_card_stamina >= 10:
            self.power_card_stamina = 0
            update['stamina'] = 0

            if next_card := self.get_next_power_card():
                update['cardData'] = {
                    "card_id": next_card.id,
                    "color": next_card.color,
                    "description": next_card.description,
                    "element": next_card.element,
                    "label": next_card.name,
                    "name": next_card.name,
                    "power_id": next_card.power_id,
                    "prompt": next_card.name,
                    "set_id": next_card.set_id,
                    "value": next_card.value
                }

            if len(self.power_card_slots) > 3:
                update['cycle'] = True

        # TODO: Check if client has no power cards anymore

        snow_ui = self.get_window('cardjitsu_snowui.swf')
        snow_ui.send_payload('updateStamina', update)

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

    def send_tip(self, phase: TipPhase) -> None:
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
