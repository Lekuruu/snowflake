
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List

if TYPE_CHECKING:
    from .penguin import Penguin

from app.data.constants import KeyModifier, KeyTarget, KeyInput, Phase
from app.data.repositories import stamps

from app.objects.ninjas import WaterNinja, SnowNinja, FireNinja, Ninja
from app.objects.collections import ObjectCollection, AssetCollection
from app.objects.enemies import Sly, Scrap, Tank, Enemy
from app.objects.gameobject import GameObject
from app.objects.sound import Sound

from twisted.python.failure import Failure
from twisted.internet import reactor

from .callbacks import CallbackHandler
from .timer import Timer
from .grid import Grid

import logging
import random
import config
import time

class Game:
    def __init__(self, fire: "Penguin", snow: "Penguin", water: "Penguin") -> None:
        self.server = fire.server
        self.water = water
        self.fire = fire
        self.snow = snow

        self.bonus_cirteria = random.choice(['no_ko', 'under_time', 'full_health'])
        self.game_start = time.time()

        self.map = random.randrange(1, 3)
        self.round = 0

        self.callbacks = CallbackHandler(self)
        self.objects = ObjectCollection()
        self.timer = Timer(self)
        self.grid = Grid(self)

        self.logger = logging.getLogger('game')

    @property
    def clients(self) -> List["Penguin"]:
        return [self.fire, self.snow, self.water]

    @property
    def ninjas(self) -> List[Ninja]:
        return [
            self.objects.by_name('Water'),
            self.objects.by_name('Snow'),
            self.objects.by_name('Fire')
        ]

    @property
    def enemies(self) -> List[Enemy]:
        return [
            *self.objects.with_name('Sly'),
            *self.objects.with_name('Scrap'),
            *self.objects.with_name('Tank')
        ]

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

    @property
    def bonus_cirteria_met(self) -> bool:
        return {
            'no_ko': all(not player.was_ko for player in self.clients),
            'full_health': all(ninja.hp == ninja.max_hp for ninja in self.ninjas),
            'under_time': (time.time() < self.game_start + 300)
        }[self.bonus_cirteria]

    def start(self) -> None:
        self.fire.game = self
        self.snow.game = self
        self.water.game = self

        # Wait for "prepare to battle" screen to end
        time.sleep(3)

        # Close player select window
        for client in self.clients:
            player_select = client.window_manager.get_window('cardjitsu_snowplayerselect.swf')
            player_select.close()

        # Register "/use" event
        self.register_input(
            command='/use',
            input_id='/use',
            script_id='4375706:1',
            target=KeyTarget.GOB,
            event=KeyInput.MOUSE_CLICK,
            key_modifier=KeyModifier.NONE
        )

        # This will trigger the loading transition
        self.send_tag(
            'W_PLACE',
            '1:10001', # PlaceId
            0,         # PlaceObjectId
            0          # PlaceInstanceId
        )

        # Scale screen up to 100
        self.send_tag('P_TILESIZE', 100)

        self.initialize_objects()
        self.wait_for_players(lambda player: player.is_ready)

        # Play background music
        Sound.from_name('mus_mg_201303_cjsnow_gamewindamb', looping=True).play(self)

        self.show_background()
        self.spawn_ninjas()

        for client in self.clients:
            # Close loading screen
            player_select = client.window_manager.get_window('cardjitsu_snowplayerselect.swf')
            player_select.send_action('closeCjsnowRoomToRoom')

            # Load exit button
            close_button = client.window_manager.get_window('cardjitsu_snowclose.swf')
            close_button.layer = 'bottomLayer'
            close_button.load(
                loadDescription="",
                assetPath="",
                xPercent=1,
                yPercent=0
            )

        # Wait for windows
        time.sleep(1)

        # Reset game time
        self.game_start = time.time() + 1

        self.display_round_title()
        time.sleep(1.6)

        self.spawn_enemies()
        time.sleep(1)

        self.show_ui()
        self.send_tip(Phase.MOVE)

        # Run game loop until game ends
        self.run_game_loop()

        time.sleep(2)
        for ninja in self.ninjas:
            if ninja.hp <= 0:
                continue

            ninja.win_animation()

        time.sleep(4)
        for ninja in self.ninjas:
            ninja.remove_object()

        self.display_payout()
        self.wait_for_players(lambda player: player.disconnected)
        self.close()

    def close(self) -> None:
        self.logger.info('Game finished.')
        # TODO: Cleanup

    def run_game_loop(self) -> None:
        while True:
            self.run_until_next_round()
            self.round += 1

            if all(ninja.hp <= 0 for ninja in self.ninjas):
                # All ninjas have been defeated
                break

            if (self.round > 2) and (not self.bonus_cirteria_met):
                break

            if (self.round > 3):
                break

            # Remove any existing enemies
            self.remove_enemies()

            # Enemies can spawn anywhere now
            self.grid.enemy_spawns = [range(9), range(5)]

            self.display_round_title()
            time.sleep(1.6)

            # Create new enemies
            self.create_enemies()
            self.spawn_enemies()
            time.sleep(1)

    def run_until_next_round(self) -> None:
        while True:
            for client in self.clients:
                client.is_ready = False

            self.show_targets()
            self.wait_for_timer()

            self.hide_ghosts()
            self.remove_targets()
            self.remove_confirm()
            time.sleep(1.25)

            self.move_ninjas()
            # TODO: Ninja attacks
            # TODO: Enemy attacks

            # NOTE: Only for testing
            self.enemies[0].set_health(0)

            # Wait for any animations to finish
            self.wait_for_animations()

            if self.check_round_completion():
                break

    def check_round_completion(self) -> bool:
        if not self.enemies:
            # Enemies have been defeated
            return True

        if all(ninja.hp <= 0 for ninja in self.ninjas):
            # All ninjas have been defeated
            return True

        return False

    def send_tag(self, tag: str, *args) -> None:
        for player in self.clients:
            player.send_tag(tag, *args)

    def wait_for_players(self, condition: Callable) -> None:
        """Wait for all players to finish loading the game"""
        for player in self.clients:
            while not condition(player) and not self.server.shutting_down:
                pass

    def wait_for_animations(self) -> None:
        """Wait for all animations to finish"""
        while self.callbacks.pending_animation_ids:
            pass

    def wait_for_timer(self) -> None:
        """Wait for the timer to finish"""
        self.grid.show_tiles()
        self.enable_cards()
        self.timer.run()
        self.grid.hide_tiles()
        self.disable_cards()

    def error_callback(self, failure: Failure) -> None:
        self.logger.error(
            f'Failed to execute game thread: {failure.getBriefTraceback()}',
            exc_info=failure.tb
        )

        for client in self.clients:
            client.send_to_room()

    def register_input(
        self,
        input_id: str,
        script_id: int,
        target: KeyTarget,
        event: KeyInput,
        key_modifier: KeyModifier,
        command: str
    ) -> None:
        self.send_tag(
            'W_INPUT',
            input_id,
            script_id,
            target.value,
            event.value,
            key_modifier.value,
            command
        )

    def initialize_objects(self) -> None:
        """Initialize all game objects"""
        self.grid.initialize_tiles()
        self.create_background()
        self.create_enemies()
        self.create_ninjas()

        # Load sprites
        for object in self.objects:
            object.load_sprites()

    def create_ninjas(self) -> None:
        water = WaterNinja(self, x=0, y=0)
        water.place_object()
        self.water.ninja = water

        fire = FireNinja(self, x=0, y=2)
        fire.place_object()
        self.fire.ninja = fire

        snow = SnowNinja(self, x=0, y=4)
        snow.place_object()
        self.snow.ninja = snow

    def create_enemies(self) -> None:
        max_enemies = {
            0: range(1, 4),
            1: range(1, 4),
            2: range(1, 4),
            3: range(4, 5),
        }[self.round]

        amount_enemies = random.choice(max_enemies)
        enemy_classes = (Sly, Scrap, Tank)

        for _ in range(amount_enemies):
            enemy_class = random.choice(enemy_classes)
            enemy = enemy_class(self)
            enemy.place_object()

    def create_background(self) -> None:
        for background in self.backgrounds:
            background.place_object()

    def spawn_ninjas(self) -> None:
        water = self.objects.by_name('Water')
        water.place_object()
        water.idle_animation()
        water.place_healthbar()

        snow = self.objects.by_name('Snow')
        snow.place_object()
        snow.idle_animation()
        snow.place_healthbar()

        fire = self.objects.by_name('Fire')
        fire.place_object()
        fire.idle_animation()
        fire.place_healthbar()

    def spawn_enemies(self) -> None:
        """Spawn enemies for the current round"""
        for enemy in self.enemies:
            # Choose spawn location on grid
            x, y = self.grid.enemy_spawn_location()

            self.grid[x, y] = enemy
            enemy.place_object()

            # Play spawn animation
            enemy.spawn()
            enemy.place_healthbar()

    def remove_enemies(self) -> None:
        for enemy in self.enemies:
            enemy.remove_object()

    def remove_ninjas(self) -> None:
        for ninja in self.ninjas:
            ninja.remove_object()

    def remove_confirm(self) -> None:
        for object in self.objects.with_name('confirm'):
            object.remove_object()

    def hide_ghosts(self) -> None:
        for ninja in self.ninjas:
            ninja.hide_ghost(reset_positions=False)

    def move_ninja(self, ninja: Ninja, x: int, y: int) -> None:
        if ninja.x == x and ninja.y == y:
            return

        if x == -1 or y == -1:
            return

        ninja.move_animation()
        ninja.idle_animation()
        ninja.move_object(x, y)
        ninja.play_sound(
            'sfx_mg_2013_cjsnow_footsteppenguin' \
                if ninja.name != 'Fire'
                else 'sfx_mg_2013_cjsnow_footsteppenguinfire'
        )

        # Reset ghost position
        ninja.ghost.x = -1
        ninja.ghost.y = -1

    def move_ninjas(self) -> None:
        for ninja in self.ninjas:
            self.move_ninja(
                ninja,
                ninja.ghost.x,
                ninja.ghost.y
            )

        # Wait for move animations
        self.wait_for_animations()

    def show_targets(self) -> None:
        for ninja in self.ninjas:
            ninja.show_targets()

    def remove_targets(self) -> None:
        for ninja in self.ninjas:
            ninja.remove_targets()

    def show_background(self) -> None:
        for background in self.backgrounds:
            obj = self.objects.by_name(background.name)
            obj.place_sprite(background.name)

    def show_ui(self) -> None:
        for client in self.clients:
            snow_ui = client.window_manager.get_window('cardjitsu_snowui.swf')
            snow_ui.layer = 'bottomLayer'
            snow_ui.load(
                {
                    'cardsAssetPath': f'http://{config.MEDIA_LOCATION}/game/mpassets//minigames/cjsnow/en_US/deploy/',
                    'element': client.element,
                    'isMember': client.is_member,
                },
                loadDescription="",
                assetPath="",
                xPercent=0.5,
                yPercent=1
            )

    def send_tip(self, phase: Phase, client: "Penguin" | None = None) -> None:
        clients = [client] if client else self.clients

        for client in clients:
            if phase in client.displayed_tips:
                return

            if not client.tip_mode:
                continue

            infotip = client.window_manager.get_window('cardjitsu_snowinfotip.swf')
            infotip.layer = 'topLayer'
            infotip.load(
                {
                    'element': client.element,
                    'phase': phase.value,
                },
                loadDescription="",
                assetPath="",
                xPercent=0.1,
                yPercent=0
            )

            client.displayed_tips.append(phase)
            client.last_tip = phase

    def enable_cards(self) -> None:
        for client in self.clients:
            snow_ui = client.window_manager.get_window('cardjitsu_snowui.swf')
            snow_ui.send_payload('enableCards')

    def disable_cards(self) -> None:
        for client in self.clients:
            snow_ui = client.window_manager.get_window('cardjitsu_snowui.swf')
            snow_ui.send_payload('disableCards')

    def display_round_title(self) -> None:
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

    def display_payout(self) -> None:
        snow_stamps = stamps.fetch_all_by_group(60)

        for client in self.clients:
            payout = client.window_manager.get_window('cardjitsu_snowpayout.swf')
            payout.layer = 'bottomLayer'
            payout.load(
                {
                    "coinsEarned": 0,     # TODO
                    "damage": 0,          # TODO
                    "doubleCoins": False, # TODO
                    "isBoss": 0,
                    "rank": client.object.snow_ninja_rank,
                    "round": self.round,
                    "showItems": 0,       # TODO
                    "stampList": [
                        {
                            "stamp_id": stamp.id,
                            "name": f'global_content.stamps.{stamp.id}.name',
                            "description": f'global_content.stamps.{stamp.id}.description',
                            "rank_token": f'global_content.stamps.{stamp.id}.rank_token',
                            "rank": stamp.rank,
                            "is_member": stamp.member,
                        }
                        for stamp in snow_stamps
                    ],
                    "stamps": [], # TODO
                    "xpEnd": client.object.snow_ninja_progress, # TODO
                    "xpStart": client.object.snow_ninja_progress,
                },
                loadDescription="",
                assetPath="",
                xPercent=0.08,
                yPercent=0.05
            )
