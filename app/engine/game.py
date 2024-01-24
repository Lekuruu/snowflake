
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .penguin import Penguin

from app.objects.collections import (
    GameObjectCollection,
    SpriteCollection,
    SoundCollection
)

import random

class Game:
    def __init__(self, fire: "Penguin", snow: "Penguin", water: "Penguin") -> None:
        self.fire = fire
        self.snow = snow
        self.water = water

        self.round = 1
        self.enemies = []
        self.map = random.randrange(1, 3)

        self.objects = GameObjectCollection()
        self.sprites = SpriteCollection()
        self.sounds = SoundCollection()

    @property
    def clients(self) -> list["Penguin"]:
        return [self.fire, self.snow, self.water]

    def start(self) -> None:
        self.fire.game = self
        self.snow.game = self
        self.water.game = self
        self.wait_for_players()
        # TODO: ...

    def wait_for_players(self) -> None:
        """Wait for all players to finish loading the game"""
        for player in self.clients:
            while not player.in_game:
                pass
