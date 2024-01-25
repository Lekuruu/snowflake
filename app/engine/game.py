
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .penguin import Penguin

from app.objects.collections import ObjectCollection
from app.objects.sprite import Sprite
from app.objects.sound import Sound

import random
import time

class Game:
    def __init__(self, fire: "Penguin", snow: "Penguin", water: "Penguin") -> None:
        self.fire = fire
        self.snow = snow
        self.water = water

        self.round = 1
        self.enemies = []
        self.map = random.randrange(1, 3)

        self.objects = ObjectCollection()

    @property
    def clients(self) -> list["Penguin"]:
        return [self.fire, self.snow, self.water]

    @property
    def backgrounds(self) -> List[str]:
        return {
            1: ['env_mountaintop_bg'],
            2: ['forest_bg', 'forest_fg'],
            3: ['cragvalley_bg', 'cragvalley_fg', 'crag_rock']
        }[self.map]

    def start(self) -> None:
        self.fire.game = self
        self.snow.game = self
        self.water.game = self

        # Wait for "prepare to battle" screen to end
        time.sleep(3)

        for client in self.clients:
            player_select = client.window_manager.get_window('cardjitsu_snowplayerselect.swf')
            player_select.close()

        # This will trigger the loading transition
        self.send_tag(
            'W_PLACE',
            '1:10001', # PlaceId
            8,         # PlaceObjectId
            1          # PlaceInstanceId
        )

        self.initialize_objects()
        self.wait_for_players()

        # TODO: Game logic

    def send_tag(self, tag: str, *args) -> None:
        for player in self.clients:
            player.send_tag(tag, *args)

    def wait_for_players(self) -> None:
        """Wait for all players to finish loading the game"""
        for player in self.clients:
            while not player.in_game:
                pass

    def initialize_objects(self) -> None:
        """Initialize all game objects"""
        # Play background music
        Sound.from_name('mus_mg_201303_cjsnow_gamewindamb', looping=True).play(self)
