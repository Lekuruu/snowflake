
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .penguin import Penguin

from app.objects.collections import ObjectCollection, AssetCollection
from app.objects.ninjas import WaterNinja, SnowNinja, FireNinja
from app.objects.enemies import Sly, Scrap, Tank, Tusk
from app.objects.gameobject import GameObject
from app.objects.sound import Sound
from app.objects.asset import Asset
from .grid import Grid

import random
import time

class Game:
    def __init__(self, fire: "Penguin", snow: "Penguin", water: "Penguin") -> None:
        self.fire = fire
        self.snow = snow
        self.water = water

        self.round = 0
        self.enemies = []
        self.map = random.randrange(1, 3)
        self.bonus_cirteria = 'under_time' # TODO: Select random
        self.game_start = time.time()

        self.objects = ObjectCollection()
        self.grid = Grid()

    @property
    def clients(self) -> List["Penguin"]:
        return [self.fire, self.snow, self.water]

    @property
    def backgrounds(self) -> List[GameObject]:
        return {
            1: [
                GameObject.from_asset('env_mountaintop_bg', self, x=4.5, y=-1.1)
            ],
            2: [
                GameObject.from_asset('forest_bg', self, x=4.5, y=-1.1),
                GameObject.from_asset('forest_fg', self, x=4.5, y=6.1)
            ],
            3: [
                GameObject.from_asset('cragvalley_bg', self, x=4.5, y=-1.1),
                GameObject.from_asset('cragvalley_fg', self, x=4.5, y=6)
            ]
        }[self.map]

    def start(self) -> None:
        self.fire.game = self
        self.snow.game = self
        self.water.game = self

        self.fire.in_game = True
        self.snow.in_game = True
        self.water.in_game = True

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

        # Scale screen up to 100
        self.send_tag('P_TILESIZE', 100)

        self.initialize_objects()
        self.wait_for_players()

        # Play background music
        Sound.from_name('mus_mg_201303_cjsnow_gamewindamb', looping=True).play(self)

        # Place background sprites
        for background in self.backgrounds:
            obj = self.objects.by_name(background.name)
            obj.place_sprite(background.name)

        water = self.objects.by_name('Water')
        water.place_object()
        water.animate_object(
            'waterninja_idle_anim',
            play_style='loop',
            reset=True
        )

        snow = self.objects.by_name('Snow')
        snow.place_object()
        snow.animate_object(
            'snowninja_idle_anim',
            play_style='loop',
            reset=True
        )

        fire = self.objects.by_name('Fire')
        fire.place_object()
        fire.animate_object(
            'fireninja_idle_anim',
            play_style='loop',
            reset=True
        )

        for client in self.clients:
            # Close loading screen
            player_select = client.window_manager.get_window('cardjitsu_snowplayerselect.swf')
            player_select.send_action('closeCjsnowRoomToRoom')

            # Close game button
            close_button = client.window_manager.get_window('cardjitsu_snowclose.swf')
            close_button.layer = 'bottomLayer'
            close_button.load(
                loadDescription="",
                assetPath="",
                xPercent=1,
                yPercent=0
            )

        # Reset game time
        self.game_start = time.time()

        # Show round title
        self.display_round_title()

    def send_tag(self, tag: str, *args) -> None:
        for player in self.clients:
            player.send_tag(tag, *args)

    def wait_for_players(self) -> None:
        """Wait for all players to finish loading the game"""
        for player in self.clients:
            while not player.is_ready:
                pass

    def initialize_objects(self) -> None:
        """Initialize all game objects"""
        # Background
        for background in self.backgrounds:
            self.objects.add(background)
            background.place_object()

        # Ninjas
        self.objects.add(water := WaterNinja(self))
        self.grid[0, 0] = water
        water.place_object()

        self.objects.add(snow := SnowNinja(self))
        self.grid[0, 2] = snow
        snow.place_object()

        self.objects.add(fire := FireNinja(self))
        self.grid[0, 4] = fire
        fire.place_object()

        # Enemies
        self.objects.add(sly := Sly(self))
        sly.place_object()

        self.objects.add(scrap := Scrap(self))
        scrap.place_object()

        self.objects.add(tank := Tank(self))
        tank.place_object()

        # Load sprites
        for object in self.objects:
            object.load_sprites()

    def display_round_title(self) -> None:
        # TODO: Implement other bonus criteria
        for client in self.clients:
            round_title = client.window_manager.get_window('cardjitsu_snowrounds.swf')
            round_title.layer = 'bottomLayer'
            round_title.load(
                {
                    'bonusCriteria': self.bonus_cirteria,
                    'remainingTime': ((self.game_start + 300) - time.time()) * 1000,
                    'roundNumber': self.round
                },
                loadDescription="",
                assetPath=""
            )
