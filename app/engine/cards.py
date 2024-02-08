
from __future__ import annotations

from app.objects import GameObject
from app.engine.game import Game
from app.data import Card

class CardObject(Card):
    def __init__(self, card: Card, game: Game) -> None:
        self.__dict__.update(card.__dict__)
        self.object = GameObject(
            game,
            card.name,
            x_offset=0.5,
            y_offset=1
        )

    def __repr__(self) -> str:
        return f'<CardObject {self.id} ({self.x}, {self.y})>'

    def place(self, x: int, y: int) -> None:
        self.object.x = x
        self.object.y = y
        self.object.place_object()
        self.object.place_sprite({
            'f': 'ui_card_fire',
            'w': 'ui_card_water',
            's': 'ui_card_snow',
        }[self.element])

    def remove(self) -> None:
        self.object.remove_object()
