
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from app.server import SnowflakeWorld
    from app.objects.ninjas import Ninja
    from app.engine.game import Game

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.python.failure import Failure
from sqlalchemy.orm import Session

from app.engine.cards import CardObject, MemberCard
from app.protocols import MetaplaceProtocol
from app.data import stamps, cards
from app.data import (
    Penguin as PenguinObject,
    EventType,
    TipPhase,
    Card
)

import app.session
import random
import config

class Penguin(MetaplaceProtocol):
    def __init__(self, server: "SnowflakeWorld", address: IPv4Address | IPv6Address):
        super().__init__(server, address)
        self.address = address
        self.server = server

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

        self.member_card: MemberCard | None = None
        self.selected_card: CardObject | None = None
        self.cards_available: List[CardObject] = []
        self.cards_placed: int = 0
        self.unlocked_stamps: List[int] = []
        self.power_card_stamina: int = 0
        self.played_cards: int = 0

        self.login_time: int = 0
        self.queue_time: int = 0

        self.mute_sounds: bool = False
        self.in_queue: bool = False
        self.is_ready: bool = False
        self.is_bot: bool = False
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
    def has_power_cards(self) -> bool:
        return bool(self.cards_available)

    @property
    def selected_member_card(self) -> bool:
        return self.member_card and self.member_card.selected

    @property
    def placed_powercard(self) -> bool:
        return bool(self.selected_card and self.selected_card.x != -1 and self.selected_card.y != -1)

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

        if self.in_game:
            # Remove any pending events
            self.game.callbacks.remove_events(self)

        # Put client in ready state, so that the game doesn't softlock
        self.is_ready = True

        return super().close_connection()

    def connectionLost(self, reason: Failure | None = None) -> None:
        if self.in_game and self.ninja and self.game.ninjas:
            self.ninja.set_health(0)

        if reason is not None and not self.disconnected:
            self.logger.warning(f"Connection lost: {reason.getErrorMessage()}")

        self.server.matchmaking.remove(self)
        self.server.players.remove(self)
        self.disconnected = True

    def send_tag(self, tag: str, *args) -> None:
        if tag.startswith('FX') and self.mute_sounds:
            return

        super().send_tag(tag, *args)

    def initialize_power_cards(self, session=None) -> None:
        card_color = {
            'snow': 'p',
            'water': 'b',
            'fire': 'r'
        }[self.element]

        element_name = {
            'snow': 's',
            'water': 'w',
            'fire': 'f'
        }[self.element]

        power_cards = cards.fetch_power_cards_by_penguin_id(
            self.pid,
            element_name,
            session=session
        )

        for card in power_cards:
            card_object = CardObject(card, self)
            card_object.color = card_color
            self.cards_available.append(card_object)

    def next_power_card(self) -> CardObject | None:
        
        if not self.has_power_cards:
            # Client has no more power cards
            self.logger.info(f'{self.name} has no more power cards')
            return

        next_card = random.choice(self.cards_available)
        self.cards_available.append(next_card)
        self.cards_available.remove(next_card)

        return next_card

    def power_card_by_id(self, card_id: int) -> Card | None:
        return next((c for c in self.cards_available if c.id == card_id), None)

    def update_cards(self) -> None:
        if self.disconnected:
            return

        if self.is_bot:
            return

        if self.has_power_cards:

            self.power_card_stamina += 2

            update = {
                'cardData': None,
                'cycle': False,
                'stamina': self.power_card_stamina
            }

            if self.power_card_stamina >= 10: # add a new card
                self.power_card_stamina = 0

                update['stamina'] = 0

                if next_card := self.next_power_card():
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

                if update['cardData'] is not None:
                    self.cards_placed += 1
                    self.logger.info(f'{self.name} added card {update['cardData']['card_id']}')

                if len(self.cards_available) > 3:
                    update['cycle'] = True

            self.logger.info(f'{self.name} stamina : {self.power_card_stamina}')

            snow_ui = self.get_window('cardjitsu_snowui.swf')
            snow_ui.send_payload('updateStamina', update)

    def consume_card(self, is_combo=False) -> None:
        if not self.selected_card:
            return

        self.selected_card.use(is_combo)

    def send_to_room(self) -> None:
        # This will load a window, that sends the player back to the room
        window = self.get_window('cardjitsu_snowexternalinterfaceconnector.swf')
        window.layer = 'toolLayer'
        window.load(type=EventType.IMMEDIATE.value)

    def send_error(self, key: str, code: int = 0, data: str = "", level: str = 'Warning') -> None:
        error_handler = self.get_window('cardjitsu_snowerrorhandler.swf')

        if not error_handler.loaded:
            error_handler.layer = 'bottomLayer'
            error_handler.load(
                xPercent=0,
                yPercent=0,
                loadDescription=""
            )

            error_handler.on_load = lambda *args: self.send_error(key, code, data)
            return

        error_handler.send_payload(
            level,
            {
                'msg': key,
                'code': code, # TODO
                'data': data # TODO
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

    def unlock_stamp(self, id: int, session: Session | None = None) -> None:
        if config.DISABLE_STAMPS:
            return

        if self.disconnected:
            return

        if not (stamp := stamps.fetch_one(id, session=session)):
            return

        if stamps.exists(id, self.pid, session=session):
            return

        self.logger.info(f'{self} unlocked stamp: "{stamp.name}"')
        self.unlocked_stamps.append(stamp.id)
        stamps.add(
            id, self.pid,
            session=session
        )

        window = self.get_window('stampearned.swf')

        # Wait for previous window to close
        self.window_manager.wait_for_window(window, loaded=False)

        # Load window
        window.load(
            {
                'stamp':
                {
                    'stamp_id': stamp.id,
                    'stampGroupId': stamp.group_id,
                    'parent_group_id': 8, # TODO
                    'name': f'global_content.stamps.{stamp.id}.name',
                    'description': f'global_content.stamps.{stamp.id}.description',
                    'rank_token': f'global_content.stamps.{stamp.id}.rank_token',
                    'is_member': stamp.member,
                    'rank': stamp.rank
                }
            },
            assetPath=f'{config.WINDOW_BASEURL}/'
        )
