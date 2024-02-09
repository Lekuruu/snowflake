
from __future__ import annotations

import time
from typing import Tuple, List, TYPE_CHECKING

from app.objects import GameObject, LocalGameObject
from app.data import Card

if TYPE_CHECKING:
    from app.engine import Penguin

class CardObject(Card):
    def __init__(self, card: Card, client: "Penguin") -> None:
        self.__dict__.update(card.__dict__)
        self.game = client.game
        self.client = client
        self.object = GameObject(
            client.game,
            card.name,
            x_offset=0.5,
            y_offset=1
        )
        self.pattern = LocalGameObject(
            client,
            'ui_card_pattern',
            x_offset=0.5,
            y_offset=1
        )

    def __repr__(self) -> str:
        return f'<CardObject {self.id} ({self.x}, {self.y})>'

    @property
    def x(self):
        return self.object.x

    @property
    def y(self):
        return self.object.y

    def place(self, x: int, y: int) -> None:
        self.place_card_sprite(x, y)
        self.place_pattern_sprite(x, y)

    def remove(self) -> None:
        self.object.remove_object()
        self.pattern.remove_object()

    def place_card_sprite(self, x: int, y: int) -> None:
        self.object.x = x
        self.object.y = y
        self.object.place_object()
        self.object.place_sprite({
            'f': 'ui_card_fire',
            'w': 'ui_card_water',
            's': 'ui_card_snow',
        }[self.element])

    def place_pattern_sprite(self, x: int, y: int) -> None:
        # Set default offsets
        self.pattern.x_offset = 0.5
        self.pattern.y_offset = 1

        x_range, y_range = self.pattern_range(x, y)

        self.pattern.x = x
        self.pattern.y = y
        self.pattern.place_object()
        self.pattern.place_sprite(f'ui_card_pattern{len(x_range)}x{len(y_range)}')

    def pattern_range(self, x: int, y: int) -> Tuple[List[int], List[int]]:
        max_x = max(*self.game.grid.x_range)
        min_x = min(*self.game.grid.x_range)
        max_y = max(*self.game.grid.y_range)
        min_y = min(*self.game.grid.y_range)

        # Get surrounding tiles of card
        x_range = range(x - 1, x + 2)
        y_range = range(y - 1, y + 2)

        # If the card is on the edge of the grid, remove the out-of-bounds tiles
        if y == min_y:
            y_range = y_range[1:]
            self.pattern.y_offset = 1

        if y == max_y:
            y_range = y_range[:-1]
            self.pattern.y_offset = 0

        if x == min_x:
            x_range = x_range[1:]
            self.pattern.x_offset = 1

        if x == max_x:
            x_range = x_range[:-1]
            self.pattern.x_offset = 0

        return x_range, y_range

    def use(self) -> None:
        if self.client.selected_card != self:
            return

        # Wait for any pending animations
        self.game.wait_for_animations()

        for client in self.game.clients:
            payload_name = 'consumeCard' if self.client == client else 'showCaseOthersCard'

            snow_ui = client.get_window('cardjitsu_snowui.swf')
            snow_ui.send_payload(payload_name)

        # Wait for client to consume card
        self.game.callbacks.wait_for_client('ConsumeCardResponse', self.client)

        # Wait for client to play the animation
        time.sleep(1)
