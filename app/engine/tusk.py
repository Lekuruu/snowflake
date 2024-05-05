
from __future__ import annotations
from typing import List

from app.objects.ninjas import WaterNinja, FireNinja, SnowNinja, Sensei
from app.objects.collections import ObjectCollection
from app.objects.gameobject import GameObject
from app.objects.enemies import Enemy, Tusk
from app.objects.ninjas import Ninja
from app.objects.sound import Sound

from app.data import TipPhase, ExpRequirements, SnowRewards
from app.data import stamps, penguins, items

from .callbacks import CallbackHandler
from .cards import MemberCard
from .penguin import Penguin
from .timer import Timer
from .game import Game
from .grid import Grid

import app.session
import logging
import random
import config
import time

class TuskGame(Game):
    def __init__(self, fire: Penguin, snow: Penguin, water: Penguin) -> None:
        self.water = water
        self.fire = fire
        self.snow = snow
        self.id = -1

        self.sensei: Sensei | None = None
        self.tusk: Tusk | None = None

        self.total_combos = 0
        self.damage = 0
        self.coins = 0
        self.round = 4
        self.exp = 0

        self.game_start = time.time()
        self.callbacks = CallbackHandler(self)
        self.objects = ObjectCollection(offset=1000)
        self.grid = Grid(9, 5, self)
        self.timer = Timer(self)

        self.server = self.clients[0].server
        self.logger = logging.getLogger('TuskGame')
        self.backgrounds = []
        self.rocks = []

    @property
    def enemies(self) -> List[Enemy]:
        return self.objects.with_name('Tusk')

    @property
    def bonus_criteria_met(self) -> bool:
        return False

    def start(self) -> None:
        with app.session.database.managed_session() as session:
            for client in self.clients:
                client.game = self

                # Initialize member card
                client.member_card = MemberCard(client)

                # Initialize power cards
                client.initialize_power_cards(session=session)

        # Wait for "prepare to battle" screen to end
        time.sleep(3)

        # Close player select window
        for client in self.clients:
            player_select = client.get_window(config.PLAYERSELECT_SWF)
            player_select.close()

        # Place clients in battle place
        battle_place = self.server.places['tusk_battle']

        for client in self.clients:
            client.switch_place(battle_place)

        # Wait for loading screen to finish
        self.callbacks.wait_for_event('roomToRoomMinTime')
        time.sleep(1)

        # Wait for players to finish loading assets
        self.wait_for_players(lambda player: player.is_ready, timeout=20)

        # Play background music
        Sound.from_name('mus_mg_201303_cjsnow_tuskthemecaveamb', looping=True).play(self)

        self.initialize_objects()
        self.show_environment()
        self.spawn_ninjas()
        self.spawn_enemies()
        self.wait_for_animations()

        for client in self.clients:
            # Close loading screen
            player_select = client.get_window(config.PLAYERSELECT_SWF)
            player_select.send_action('closeCjsnowRoomToRoom')

            # Load exit button
            close_button = client.get_window('cardjitsu_snowclose.swf')
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
        self.wait_for_window('cardjitsu_snowrounds.swf', loaded=False)

        self.show_ui()
        self.send_tip(TipPhase.MOVE)

        for client in self.disconnected_clients:
            client.ninja.set_health(0)

        for client in self.clients:
            if client.has_power_cards:
                continue

            snow_ui = client.get_window('cardjitsu_snowui.swf')
            snow_ui.send_payload('noCards')

        # Run game loop until game ends
        self.run_game_loop()

        self.remove_ui()
        self.remove_targets()
        self.display_win_sequence()

        self.display_payout()
        self.remove_objects()
        self.close()

    def create_environment(self) -> None:
        self.backgrounds.append(GameObject(self, 'tusk_background_under', x=4.5, y=-1.1))
        self.backgrounds.append(GameObject(self, 'tusk_background_over', x=4.5, y=6.125))

        for background in self.backgrounds:
            background.place_object()

    def create_ninjas(self) -> None:
        spawn_positions = [
            {'x': 0, 'y': 1},
            {'x': 1, 'y': 2},
            {'x': 0, 'y': 3}
        ]

        # Randomize spawn positions
        random.shuffle(spawn_positions)

        ninja_classes = {
            'snow': SnowNinja,
            'fire': FireNinja,
            'water': WaterNinja
        }

        for index, client in enumerate(self.clients):
            element = client.element
            ninja_class = ninja_classes[element]

            ninja = ninja_class(client, **spawn_positions[index])
            ninja.place_object()
            client.ninja = ninja

        sensei = Sensei(self, x=0, y=2)
        sensei.place_object()
        self.sensei = sensei

    def create_enemies(self) -> None:
        tusk = Tusk(self, x=8, y=2)
        tusk.place_object()
        self.tusk = tusk

        # Change max hp based on player count
        max_hp = {
            1: 300,
            2: 500,
            3: 800
        }[len(self.connected_clients)]

        self.tusk.max_hp = max_hp
        self.tusk.hp = max_hp

    def spawn_ninjas(self) -> None:
        super().spawn_ninjas()
        self.sensei.place_object()
        self.sensei.idle_animation()

    def spawn_enemies(self) -> None:
        self.tusk.place_object()
        self.tusk.idle_animation()
        self.tusk.place_healthbar()

    def remove_objects(self) -> None:
        super().remove_objects()
        self.tusk.remove_object()
        self.sensei.remove_object()

    def do_powercard_attacks(self) -> None:
        ninjas_with_cards = [
            ninja for ninja in self.ninjas
            if ninja.client.placed_powercard
        ]

        elements = [
            ninja.client.element
            for ninja in ninjas_with_cards
        ]

        if self.sensei.power_state == 2:
            # Sensei is using a powerup
            elements.append('sensei')

        is_combo = len(elements) > 1

        if is_combo:
            self.total_combos += 1

            if len(ninjas_with_cards) >= 3:
                # Unlock "3 Ninja Combo stamp"
                self.unlock_stamp(467)

            if self.total_combos >= 3:
                # Unlock "3 Combos" stamp
                self.unlock_stamp(485)

            if len(elements) >= 4:
                # Unlock "4 Ninja Combo" stamp
                self.unlock_stamp(468)

            self.display_combo_title(elements)
            self.callbacks.wait_for_event('comboScreenComplete', timeout=6)

        self.sensei.update_state()
        time.sleep(1)

        for ninja in ninjas_with_cards:
            ninja.use_powercard(is_combo)
            time.sleep(1)

    def display_round_title(self) -> None:
        for client in self.clients:
            round_title = client.get_window('cardjitsu_snowrounds.swf')
            round_title.layer = 'bottomLayer'
            round_title.load(
                {'roundNumber': self.round},
                loadDescription="",
                assetPath="",
                xPercent=0.15,
                yPercent=0.15
            )

        self.wait_for_window('cardjitsu_snowrounds.swf', loaded=True)

    def display_payout(self) -> None:
        with app.session.database.managed_session() as session:
            snow_stamps = stamps.fetch_all_by_group(60, session=session)

            for client in self.clients:
                if client.disconnected:
                    continue

                if client.object.snow_ninja_rank < 24:
                    required_exp = ExpRequirements.get(client.object.snow_ninja_rank, 3000)
                    current_exp = round((client.object.snow_ninja_progress / 100) * required_exp)

                    # Calculate new exp
                    result_exp = current_exp + self.exp
                    exp_percentage = round(result_exp / required_exp * 100)

                    # Calculate new rank
                    ranks_gained = exp_percentage // 100
                    result_rank = round(client.object.snow_ninja_rank + ranks_gained)

                else:
                    # Clamp rank to 24
                    result_rank = 24
                    exp_percentage = 100

                # Enable double coins when player has unlocked all stamps
                double_coins = stamps.completed_group(client.pid, 60, session=session)
                coins = self.coins * (2 if double_coins else 1)

                updates = {
                    'coins': client.object.coins + coins,
                    'snow_ninja_rank': result_rank,
                    'snow_ninja_progress': exp_percentage % 100
                }

                if len(self.enemies) <= 0:
                    # Update win count
                    key = f'snow_progress_{client.element}_wins'
                    wins = getattr(client.object, key, 0)
                    updates[key] = wins + 1

                if not config.DISABLE_REWARDS:
                    # Update penguin data
                    penguins.update(
                        client.pid, updates,
                        session=session
                    )

                    if result_rank != client.object.snow_ninja_rank:
                        self.logger.info(f'{client} ranked up from {client.object.snow_ninja_rank} to {result_rank}')

                    for rank in range(client.object.snow_ninja_rank + 1, result_rank + 1):
                        if not (item := SnowRewards.get(rank)):
                            continue

                        # Add item to inventory
                        items.add(
                            client.pid, item,
                            session=session
                        )

                        self.logger.info(f'{client} unlocked item {item}')

                    if not self.enemies:
                        # Award "Tusk's Cloak" item
                        items.add(
                            client.pid, 3160,
                            session=session
                        )

                        self.logger.info(f'{client} unlocked item 3160')

                # Display payout swf window
                payout = client.get_window('cardjitsu_snowpayout.swf')
                payout.layer = 'bottomLayer'
                payout.load(
                    {
                        "coinsEarned": coins,
                        "doubleCoins": double_coins,
                        "damage": min(self.damage, 100),
                        "isBoss": 1,
                        "rank": client.object.snow_ninja_rank + 1,
                        "round": self.get_payout_round(),
                        "showItems": 1,
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
                                "new": stamp.id in client.unlocked_stamps
                            }
                            for stamp in stamps.fetch_by_penguin_id(client.pid, 60)
                        ],
                        "xpStart": client.object.snow_ninja_progress,
                        "xpEnd": exp_percentage if result_rank < 24 else 100,
                    },
                    loadDescription="",
                    assetPath="",
                    xPercent=0.08,
                    yPercent=0.05
                )

    def display_win_sequence(self) -> None:
        time.sleep(2)

        if all(ninja.hp <= 0 for ninja in self.ninjas):
            self.tusk.win_animation()
            self.sensei.lose_animation()
            self.wait_for_animations()
            return

        # Unlock "Final Battle" stamp
        self.unlock_stamp(486)

        for ninja in self.ninjas:
            if ninja.client.disconnected:
                continue

            if ninja.hp <= 0:
                ninja.set_health(1)

            ninja.win_animation()

        self.sensei.win_animation()

        time.sleep(3.5)
