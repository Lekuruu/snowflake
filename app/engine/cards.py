
from app.objects import GameObject
from app.engine.game import Game
from app.data import Card

class CardObject(Card):
    def __init__(self, card: Card, game: Game) -> None:
        self.__dict__.update(card.__dict__)
        self.object = GameObject(game, card.name)

    def __repr__(self) -> str:
        return f'<CardObject {self.id} ({self.x}, {self.y})>'

    @property
    def x(self):
        return self.object.x

    @x.setter
    def x(self, value):
        self.object.x = value

    @property
    def y(self):
        return self.object.y

    @y.setter
    def y(self, value):
        self.object.y = value

    def place(self) -> None:
        ...
