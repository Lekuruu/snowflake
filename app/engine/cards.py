
from __future__ import annotations
from typing import Tuple, List, TYPE_CHECKING

from app.data import Card
from app.objects import GameObject, LocalGameObject
from app.objects.ninjas import Ninja
from app.objects.enemies import Enemy
from app.objects.effects import (
    WaterPowerBeam,
    FirePowerBeam,
    SnowPowerBeam,
    FirePowerBottle,
    WaterFishDrop,
    SnowIgloo
)

import time

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

        # Add delay before card gets played
        time.sleep(0.5)

        for client in self.game.clients:
            payload_name = 'consumeCard'
            data = {}

            if self.client != client:
                payload_name = 'showCaseOthersCard'
                data["cardData"] = {
                    "card_id": self.id,
                    "color": self.color,
                    "description": self.description,
                    "element": self.element,
                    "label": self.name,
                    "name": self.name,
                    "power_id": self.power_id,
                    "prompt": self.name,
                    "set_id": self.set_id,
                    "value": self.value
                }

            snow_ui = client.get_window('cardjitsu_snowui.swf')
            snow_ui.send_payload(payload_name, data)

        # Wait for client to consume card
        self.game.callbacks.wait_for_client('ConsumeCardResponse', self.client)

        # Wait for client to play the animation
        time.sleep(1.2)

        self.client.ninja.power_animation()

        beam_class = {
            'fire': FirePowerBeam,
            'water': WaterPowerBeam,
            'snow': SnowPowerBeam
        }[self.client.element]

        beam = beam_class(self.game, self.client.ninja.x, self.client.ninja.y)
        beam.play()

        impact_class = {
            'fire': FirePowerBottle,
            'water': WaterFishDrop,
            'snow': SnowIgloo
        }[self.client.element]

        impact = impact_class(self.game, self.x, self.y)
        impact.play()

        time.sleep(impact.duration)
        impact.remove_object()
        beam.remove_object()

        x_range, y_range = self.pattern_range(self.x, self.y)

        targets = [
            self.game.grid[x, y]
            for x in x_range
            for y in y_range
        ]

        for target in targets:
            if isinstance(target, Ninja) and self.client.element == 'snow':
                if target.client.disconnected:
                    continue

                target.set_health(target.hp + self.value)
                continue

            if isinstance(target, Enemy):
                # TODO: Figure out how much damage to deal
                target.set_health(target.hp - self.client.ninja.attack, wait=False)

        # TODO: Effects

        self.game.wait_for_animations()
