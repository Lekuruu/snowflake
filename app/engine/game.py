
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List

if TYPE_CHECKING:
    from .penguin import Penguin

from app.data.constants import KeyModifier, KeyTarget, KeyInput, Phase
from app.data.repositories import stamps

from app.objects.ninjas import WaterNinja, SnowNinja, FireNinja, Ninja
from app.objects.enemies import Sly, Scrap, Tank, Enemy
from app.objects.collections import ObjectCollection
from app.objects.gameobject import GameObject
from app.objects.sound import Sound

from .callbacks import CallbackHandler
from .timer import Timer
from .grid import Grid

import app.session
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
        self.id = -1

        self.bonus_cirteria = random.choice(['no_ko', 'under_time', 'full_health'])
        self.game_start = time.time()

        self.map = random.randint(1, 3)
        self.round = 0

        self.callbacks = CallbackHandler(self)
        self.objects = ObjectCollection()
        self.timer = Timer(self)
        self.grid = Grid(self)

        self.logger = logging.getLogger('Game')
        self.backgrounds = []
        self.rocks = []

    @property
    def clients(self) -> List["Penguin"]:
        return [self.fire, self.snow, self.water]

    @property
    def disconnected_clients(self) -> List["Penguin"]:
        return [client for client in self.clients if client.disconnected]

    @property
    def ninjas(self) -> List[Ninja]:
        return [
            self.objects.by_name('Fire'),
            self.objects.by_name('Water'),
            self.objects.by_name('Snow'),
        ]

    @property
    def enemies(self) -> List[Enemy]:
        return [
            *self.objects.with_name('Sly'),
            *self.objects.with_name('Scrap'),
            *self.objects.with_name('Tank')
        ]

    @property
    def bonus_cirteria_met(self) -> bool:
        return {
            'no_ko': all(not player.was_ko for player in self.clients),
            'full_health': all(ninja.hp == ninja.max_hp for ninja in self.ninjas),
            'under_time': (time.time() < self.game_start + 300)
        }[self.bonus_cirteria]

    def start(self) -> None:
        for client in self.clients:
            client.game = self

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

        # Scale screen up to 100
        self.send_tag('P_TILESIZE', 100)

        # Load assets
        self.load_assets()

        # This will trigger the loading transition
        self.send_tag(
            'W_PLACE',
            '1:10001', # PlaceId
            0,         # PlaceObjectId
            0          # PlaceInstanceId
        )

        self.initialize_objects()
        self.wait_for_players(lambda player: player.is_ready)

        # Play background music
        Sound.from_name('mus_mg_201303_cjsnow_gamewindamb', looping=True).play(self)

        self.show_environment()
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

        for client in self.disconnected_clients:
            client.ninja.set_health(0)

        # Run game loop until game ends
        self.run_game_loop()

        self.remove_confirm()
        self.remove_targets()
        self.display_win_sequence()

        self.display_payout()
        self.remove_objects()
        self.close()

    def close(self) -> None:
        self.logger.info('Game closed')
        self.server.games.remove(self)
        self.wait_for_players(lambda player: player.disconnected)
        exit()

    def run_game_loop(self) -> None:
        while True:
            self.logger.info(
                f'Starting round {self.round + 1} '
                f'({len(self.enemies)} {"enemies" if len(self.enemies) > 1 else "enemy"})'
            )

            self.run_until_next_round()
            self.round += 1

            if all(client.disconnected for client in self.clients):
                # All players have disconnected
                self.close()

            if all(ninja.hp <= 0 for ninja in self.ninjas):
                # All ninjas have been defeated
                break

            if (self.round > 2) and (not self.bonus_cirteria_met):
                # Bonus criteria not met on round 3
                break

            if (self.round > 3):
                # Bonus round completed
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
            self.remove_confirm()
            self.hide_targets()
            time.sleep(1.25)

            # Sometimes the targets are still visible?
            self.hide_targets()
            self.remove_confirm()

            self.move_ninjas()
            self.do_ninja_actions()
            self.do_enemy_actions()

            # Check if any ninja is getting revived
            for ninja in self.ninjas:
                if not isinstance(ninja.selected_object, Ninja):
                    continue

                if ninja.selected_object.hp > 0:
                    # Ninja was already revived
                    ninja.idle_animation()
                    continue

                if ninja.client.disconnected:
                    # Ninja disconnected
                    ninja.idle_animation()
                    continue

                self.wait_for_animations()
                ninja.selected_object.set_health(1)
                ninja.targets = []
                ninja.idle_animation()

            # Wait for any animations to finish
            self.wait_for_animations()

            if self.check_round_completion():
                break

    def check_round_completion(self) -> bool:
        if self.server.shutting_down:
            self.close()

        if all(client.disconnected for client in self.clients):
            self.close()

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
        while self.callbacks.pending_animations:
            pass

    def wait_for_timer(self) -> None:
        """Wait for the timer to finish"""
        self.grid.show_tiles()
        self.enable_cards()
        self.timer.run()
        self.grid.hide_tiles()
        self.disable_cards()

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

    def load_assets(self) -> None:
        # Load sprites
        for asset in app.session.assets:
            self.send_tag(
                'S_LOADSPRITE',
                f'0:{asset.index}'
            )

        # Load sounds
        for sound in app.session.sound_assets:
            self.send_tag(
                'S_LOADSPRITE',
                f'0:{sound.index}'
            )

    def initialize_objects(self) -> None:
        self.grid.initialize_tiles()
        self.create_environment()
        self.create_enemies()
        self.create_ninjas()

    def create_ninjas(self) -> None:
        water = WaterNinja(self.water, x=0, y=0)
        water.place_object()
        self.water.ninja = water

        fire = FireNinja(self.fire, x=0, y=2)
        fire.place_object()
        self.fire.ninja = fire

        snow = SnowNinja(self.snow, x=0, y=4)
        snow.place_object()
        self.snow.ninja = snow

    def create_enemies(self) -> None:
        if self.round > 3:
            return

        max_enemies = {
            0: range(1, 4),
            1: range(1, 4),
            2: range(1, 4),
            3: range(4, 5)
        }[self.round]

        amount_enemies = random.choice(max_enemies)
        enemy_classes = (Sly, Scrap, Tank)

        for _ in range(amount_enemies):
            while True:
                enemy_class = random.choice(enemy_classes)

                existing_enemies = [
                    enemy for enemy in self.enemies
                    if isinstance(enemy, enemy_class)
                ]

                # There can't be more than 3 enemies of the same type 
                if len(existing_enemies) <= 3:
                    break

            enemy = enemy_class(self)
            enemy.place_object()

    def create_environment(self) -> None:
        self.backgrounds = {
            1: [
                GameObject(self, 'env_mountaintop_bg', x=4.5, y=-1.1)
            ],
            2: [
                GameObject(self, 'forest_bg', x=4.5, y=-1.1),
                GameObject(self, 'forest_fg', x=4.5, y=6.1)
            ],
            3: [
                GameObject(self, 'cragvalley_bg', x=4.5, y=-1.1),
                GameObject(self, 'cragvalley_fg', x=4.5, y=6)
            ]
        }[self.map]

        for background in self.backgrounds:
            background.place_object()

        rock_name = 'crag_rock' if self.map == 3 else 'rock_mountaintop'
        rock_positions = [(2, 0), (6, 0), (2, 4), (6, 4)]

        self.rocks = [
            GameObject(
                self,
                rock_name,
                x, y,
                x_offset=0.5,
                y_offset=1,
                grid=True
            )
            for x, y in rock_positions
        ]

        for rock in self.rocks:
            rock.place_object()

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
        for object in self.objects.with_name('ui_confirm'):
            object.remove_object()

    def hide_ghosts(self) -> None:
        for ninja in self.ninjas:
            ninja.hide_ghost(reset_positions=False)

    def move_ninjas(self) -> None:
        for ninja in self.ninjas:
            ninja.move_ninja(
                ninja.ghost.x,
                ninja.ghost.y
            )

        # Wait for move animations
        self.wait_for_animations()

    def show_targets(self) -> None:
        for ninja in self.ninjas:
            ninja.show_targets()

    def hide_targets(self) -> None:
        for ninja in self.ninjas:
            ninja.hide_targets()

    def remove_targets(self) -> None:
        for ninja in self.ninjas:
            ninja.remove_targets()

    def show_environment(self) -> None:
        for background in self.backgrounds:
            obj = self.objects.by_id(background.id)
            obj.place_sprite(background.name)

        for rock in self.rocks:
            obj = self.objects.by_id(rock.id)
            obj.place_sprite(rock.name)

    def remove_objects(self) -> None:
        self.remove_targets()
        self.remove_confirm()

        for ninja in self.ninjas:
            ninja.remove_object()

        for enemy in self.enemies:
            enemy.remove_object()

        for rock in self.rocks:
            rock.remove_object()

    def do_ninja_actions(self) -> None:
        for ninja in self.ninjas:
            if not ninja.selected_target:
                continue

            target = ninja.selected_target.object

            if target is None:
                # Target has been removed/defeated
                continue

            if isinstance(target, Enemy):
                ninja.attack_target(target)
            else:
                ninja.heal_target(target)

            time.sleep(1)

    def do_enemy_actions(self) -> None:
        self.wait_for_animations()

        if config.DISABLE_ENEMY_AI:
            return

        for enemy in self.enemies:
            time.sleep(0.5)

            if enemy.hp <= 0:
                continue

            next_move, target = enemy.next_target()

            if not next_move:
                continue

            enemy.move_enemy(next_move.x, next_move.y)
            self.wait_for_animations()

            if target is None:
                continue

            target_object = self.grid[target.x, target.y]

            if target_object is None:
                continue

            if target_object.hp <= 0:
                continue

            enemy.attack_target(target_object)
            self.wait_for_animations()

    def show_ui(self) -> None:
        for client in self.clients:
            snow_ui = client.window_manager.get_window('cardjitsu_snowui.swf')
            snow_ui.layer = 'bottomLayer'
            snow_ui.load(
                {
                    'cardsAssetPath': f'{config.MEDIA_LOCATION}/game/mpassets//minigames/cjsnow/en_US/deploy/',
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

            def after_close(client: "Penguin"):
                client.send_tip(phase)

            if client.last_tip != None:
                # Wait for infotip to close
                infotip = client.window_manager.get_window('cardjitsu_snowinfotip.swf')
                infotip.on_close = after_close
                return

            client.displayed_tips.append(phase)
            client.send_tip(phase)

    def hide_tip(self, client: "Penguin") -> None:
        client.hide_tip()

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
                assetPath="",
                xPercent=0.15,
                yPercent=0.15
            )

    def get_payout_round(self) -> int:
        """Get the round number for the payout screen"""
        if not self.enemies and self.round == 3:
            # Players have defeated all enemies
            return 4

        elif self.round > 3:
            # Players have entered bonus round
            return 9 - len(self.enemies)

        # Players have been defeated
        return self.round

    def display_payout(self) -> None:
        snow_stamps = stamps.fetch_all_by_group(60)

        for client in self.clients:
            payout = client.window_manager.get_window('cardjitsu_snowpayout.swf')
            payout.layer = 'bottomLayer'
            payout.load(
                {
                    "coinsEarned": 0,     # TODO: Implement coins system
                    "doubleCoins": False, # TODO
                    "damage": 0,          # Only important for tusk battle
                    "isBoss": 0,
                    "rank": client.object.snow_ninja_rank,
                    "round": self.get_payout_round(),
                    "showItems": 0,       # TODO: This will show the unlocked item(s)
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
                    "stamps": [
                        {
                            "_id": stamp.id,
                            "new": False # TODO
                        }
                        for stamp in stamps.fetch_by_penguin_id(client.pid, 60)
                    ],
                    "xpEnd": client.object.snow_ninja_progress, # TODO: Implement xp system
                    "xpStart": client.object.snow_ninja_progress,
                },
                loadDescription="",
                assetPath="",
                xPercent=0.08,
                yPercent=0.05
            )

    def display_win_sequence(self) -> None:
        time.sleep(2)

        if all(ninja.hp <= 0 for ninja in self.ninjas):
            return

        for ninja in self.ninjas:
            if ninja.hp <= 0:
                ninja.set_health(1)

            ninja.win_animation()

        time.sleep(2.5)
