
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List

if TYPE_CHECKING:
    from .penguin import Penguin

from app.data.repositories import stamps, penguins, items
from app.data import (
    ExpRequirements,
    InputModifier,
    InputTarget,
    SnowRewards,
    MirrorMode,
    InputType,
    TipPhase
)

from app.objects.ninjas import WaterNinja, SnowNinja, FireNinja, Ninja
from app.objects.enemies import Sly, Scrap, Tank, Enemy
from app.objects.collections import ObjectCollection
from app.objects.gameobject import GameObject
from app.objects.sound import Sound

from .callbacks import CallbackHandler
from .cards import MemberCard
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

        self.bonus_criteria = random.choice(['no_ko', 'under_time', 'full_health'])
        self.game_start = time.time()

        self.map = random.randint(1, 3)
        self.total_combos = 0
        self.round = 0
        self.coins = 0
        self.exp = 0

        self.callbacks = CallbackHandler(self)
        self.objects = ObjectCollection(offset=1000)
        self.grid = Grid(9, 5, self)
        self.timer = Timer(self)

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
    def connected_clients(self) -> List["Penguin"]:
        return [client for client in self.clients if not client.disconnected]

    @property
    def ninjas(self) -> List[Ninja]:
        return [
            *self.objects.with_name('Fire'),
            *self.objects.with_name('Water'),
            *self.objects.with_name('Snow')
        ]

    @property
    def enemies(self) -> List[Enemy]:
        return [
            *self.objects.with_name('Sly'),
            *self.objects.with_name('Scrap'),
            *self.objects.with_name('Tank')
        ]

    @property
    def bonus_criteria_met(self) -> bool:
        return {
            'no_ko': all(not player.was_ko for player in self.clients if not player.disconnected),
            'full_health': all(ninja.hp == ninja.max_hp for ninja in self.ninjas if not ninja.client.disconnected),
            'under_time': (time.time() < self.game_start + 300)
        }[self.bonus_criteria]

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
        battle_place = self.server.places['snow_battle']

        for client in self.clients:
            client.switch_place(battle_place)

        # Wait for loading screen to finish
        self.callbacks.wait_for_event('roomToRoomMinTime')
        time.sleep(1)

        # Wait for players to finish loading assets
        self.wait_for_players(lambda player: player.is_ready, timeout=20)

        # Play background music
        Sound.from_name('mus_mg_201303_cjsnow_gamewindamb', looping=True).play(self)

        self.initialize_objects()
        self.show_environment()
        self.spawn_ninjas()

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
        time.sleep(1.6)

        self.spawn_enemies()
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

        if not self.enemies:
            for client in self.clients:
                if not client.was_ko:
                    continue

                # Unlock "Up and at 'em" stamp
                client.unlock_stamp(475)

            if all(client.was_ko for client in self.clients):
                # Unlock "Team Revival" stamp
                self.unlock_stamp(476)

            if self.round >= 3:
                # Unlock "Bonus Win" stamp
                self.unlock_stamp(473)

        self.display_payout()
        self.remove_objects()
        self.close()

    def close(self) -> None:
        self.logger.info('Game closed')
        self.server.games.remove(self)
        exit()

    def run_game_loop(self) -> None:
        while True:
            self.logger.info(
                f'Starting round {self.round + 1} '
                f'({len(self.enemies)} {"enemies" if len(self.enemies) > 1 else "enemy"})'
            )

            self.run_until_next_round()

            if all(client.disconnected for client in self.clients):
                # All players have disconnected
                self.close()

            if all(ninja.hp <= 0 for ninja in self.ninjas):
                # All ninjas have been defeated
                break

            # See: https://github.com/Lekuruu/snowflake/issues/23
            coins = {
                0: 60,
                1: 120,
                2: 120,
                3: 120
            }
            exp = {
                0: 100,
                1: 200,
                2: 300,
                3: 180
            }

            self.coins += coins.get(self.round, 0)
            self.exp += exp.get(self.round, 0)

            if (self.round >= 2) and (not self.bonus_criteria_met):
                # Bonus criteria not met on round 3
                break

            if (self.round >= 3):
                # Bonus round completed
                break

            self.round += 1

            if self.round >= 3 and self.bonus_criteria == 'full_health':
                # Unlock "Full Health" stamp
                self.unlock_stamp(472)

            # Remove any existing enemies
            self.remove_enemies()

            self.display_round_title()
            time.sleep(1.6)

            # Create new enemies
            self.create_enemies()
            self.spawn_enemies()
            self.wait_for_window('cardjitsu_snowrounds.swf', loaded=False)

    def run_until_next_round(self) -> None:
        while True:
            for client in self.clients:
                client.selected_card = None
                client.is_ready = False

                # Reset ninja's rotation, if necessary
                client.ninja.reset_sprite_settings()

                if client.power_card_slots:
                    self.send_tip(TipPhase.CARD, client)

            self.show_targets()
            self.wait_for_timer()

            self.hide_ghosts()
            self.remove_ui()
            self.hide_targets()
            time.sleep(1.25)

            # Sometimes the targets are still visible?
            self.hide_targets()
            self.remove_ui()

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

                # Unlock "revive" stamp for every ninja that was reviving this round
                for client in self.clients:
                    if client.disconnected:
                        continue

                    if client.ninja.selected_object != ninja.selected_object:
                        continue

                    client.unlock_stamp(474)

                self.wait_for_animations()
                ninja.selected_object.set_health(1)
                ninja.targets = []
                ninja.idle_animation()

            # Update enemy flame
            for enemy in self.enemies:
                enemy.update_flame()

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

    def wait_for_players(self, condition: Callable, timeout=8) -> None:
        """Wait for all players to finish a condition"""
        start_time = time.time()

        for player in self.clients:
            if player.disconnected:
                continue

            while not condition(player) and not self.server.shutting_down:
                if time.time() - start_time > timeout:
                    self.logger.warning(f'Player Timeout: {player}')
                    return

                time.sleep(0.05)

    def wait_for_animations(self, timeout=8) -> None:
        """Wait for all animations to finish"""
        start_time = time.time()

        while self.callbacks.pending_animations:
            if time.time() - start_time > timeout:
                self.logger.warning(f'Animation Timeout: {self.callbacks.pending_animations}')
                self.callbacks.reset_animations()
                break

            time.sleep(0.05)

    def wait_for_window(self, name: str, loaded=True, timeout=8) -> None:
        """Wait for a window to load/close"""
        for client in self.clients:
            window = client.get_window(name)
            start_time = time.time()

            while window.loaded != loaded:
                if client.disconnected:
                    break

                if time.time() - start_time > timeout:
                    self.logger.warning(f'Window Timeout: {name}')
                    break

            time.sleep(0.05)

    def wait_for_timer(self) -> None:
        """Wait for the timer to finish"""
        self.grid.show_tiles()
        self.enable_cards()
        self.timer.run()
        self.grid.hide_tiles()
        self.disable_cards()

    def initialize_objects(self) -> None:
        self.grid.initialize_tiles()
        self.create_environment()
        self.create_enemies()
        self.create_ninjas()

    def create_ninjas(self) -> None:
        spawn_positions = [
            {'x': 0, 'y': 0},
            {'x': 0, 'y': 2},
            {'x': 0, 'y': 4}
        ]

        # Randomize spawn positions
        random.shuffle(spawn_positions)

        water = WaterNinja(self.water, **spawn_positions[0])
        water.place_object()
        self.water.ninja = water

        fire = FireNinja(self.fire, **spawn_positions[1])
        fire.place_object()
        self.fire.ninja = fire

        snow = SnowNinja(self.snow, **spawn_positions[2])
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
        if config.ENABLE_BETA:
            # Only one map was available in beta
            self.map = 1

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

    def remove_ui(self) -> None:
        for object in self.objects.with_name('ui_confirm'):
            object.remove_object()

        for client in self.clients:
            if not client.selected_card:
                continue

            client.selected_card.remove()

        for client in self.clients:
            if not client.selected_member_card:
                continue

            client.member_card.remove()

    def hide_ghosts(self) -> None:
        for ninja in self.ninjas:
            ninja.hide_ghost(reset_positions=False)

    def move_ninjas(self) -> None:
        for ninja in self.ninjas:
            if ninja.placed_ghost:
                ninja.client.update_cards()

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
        self.remove_ui()

        for ninja in self.ninjas:
            ninja.remove_object()

            if ninja.shield:
                ninja.shield.remove_object()

            if ninja.rage:
                ninja.rage.remove_object()

        for enemy in self.enemies:
            enemy.remove_object()

            if enemy.flame:
                enemy.flame.remove_object()

        for rock in self.rocks:
            rock.remove_object()

    def do_ninja_actions(self) -> None:
        self.do_ninja_attacks()
        self.do_powercard_attacks()
        self.do_ninja_revive()
        self.wait_for_animations()

    def do_ninja_attacks(self) -> None:
        ninjas_without_cards = [
            ninja for ninja in self.ninjas
            if not ninja.client.selected_card
            and not ninja.client.selected_member_card
        ]

        for ninja in ninjas_without_cards:
            if ninja.selected_target:
                target = ninja.selected_object

                if target is None:
                    # Target has been removed/defeated
                    continue

                if isinstance(target, Enemy):
                    ninja.attack_target(target)

                if isinstance(target, Ninja):
                    ninja.heal_target(target)

                if ninja.heals >= 15:
                    # Unlock "Heal 15" stamp
                    self.snow.unlock_stamp(477)

                time.sleep(1)

    def do_powercard_attacks(self) -> None:
        ninjas_with_cards = [
            ninja for ninja in self.ninjas
            if ninja.client.placed_powercard
        ]

        is_combo = len(ninjas_with_cards) > 1

        if is_combo:
            self.total_combos += 1

            if len(ninjas_with_cards) >= 3:
                # Unlock "3 Ninja Combo stamp"
                self.unlock_stamp(467)

            if self.total_combos >= 3:
                # Unlock "3 Combos" stamp
                self.unlock_stamp(485)

            self.display_combo_title([
                ninja.client.element
                for ninja in ninjas_with_cards
            ])

            self.callbacks.wait_for_event('comboScreenComplete', timeout=6)

        for ninja in ninjas_with_cards:
            ninja.use_powercard(is_combo)
            time.sleep(1)

    def do_ninja_revive(self) -> None:
        ninjas_with_member_cards = [
            client for client in self.clients
            if client.selected_member_card
        ]

        if ninjas_with_member_cards:
            for client in self.clients:
                if client.disconnected:
                    continue

                revive_splash = client.get_window('cardjitsu_snowrevive.swf')
                revive_splash.load(
                    xPercent=0.2,
                    yPercent=0
                )

            # Wait for revive splash to load and close
            self.wait_for_window('cardjitsu_snowrevive.swf', loaded=True)
            self.wait_for_window('cardjitsu_snowrevive.swf', loaded=False)

            for ninja in ninjas_with_member_cards:
                ninja.member_card.consume()
                time.sleep(1)

    def do_enemy_actions(self) -> None:
        if config.DISABLE_ENEMY_AI:
            return

        for enemy in self.enemies:
            time.sleep(0.5)

            if enemy.hp <= 0:
                # Enemy is dead
                continue

            next_move, target = enemy.next_target()

            if not next_move and not target:
                # Enemy is stuck
                continue

            if enemy.stunned:
                # Enemy was stunned by a fire ninja
                continue

            if next_move:
                enemy.move_enemy(next_move.x, next_move.y)
                self.wait_for_animations()

            if target is None:
                # Set sprite to default direction
                enemy.reset_sprite_settings()
                continue

            target_object = self.grid[target.x, target.y]

            if target_object is None:
                # Ninja doesn't exist?
                continue

            if target_object.hp <= 0:
                # Ninja was ko'd
                continue

            if target_object.x < enemy.x:
                # Enemy's sprite might be flipped to wrong direction
                enemy.reset_sprite_settings()

            enemy.attack_target(target_object)

            if target_object.x > enemy.x:
                # Flip ninja's sprite to face the enemy
                target_object.mirror_mode = MirrorMode.X

            self.wait_for_animations()
            target_object.reset_sprite_settings()

        # Remove enemy stunned state
        for enemy in self.enemies:
            if not enemy.stunned:
                continue

            enemy.stunned = False
            enemy.idle_animation()

    def show_ui(self) -> None:
        for client in self.clients:
            snow_ui = client.get_window('cardjitsu_snowui.swf')
            snow_ui.layer = 'bottomLayer'
            snow_ui.load(
                {
                    'cardsAssetPath': config.CARDS_ASSET_LOCATION,
                    'element': client.element,
                    'isMember': client.is_member,
                },
                loadDescription="",
                assetPath="",
                xPercent=0.5,
                yPercent=1
            )

        self.wait_for_window('cardjitsu_snowui.swf', loaded=True)

    def send_tip(self, phase: TipPhase, client: "Penguin" | None = None) -> None:
        clients = [client] if client else self.clients

        for client in clients:
            if phase in client.displayed_tips:
                return

            if not client.tip_mode:
                continue

            client.displayed_tips.append(phase)

            def after_close(client: "Penguin"):
                client.send_tip(phase)

            if client.last_tip != None:
                # Wait for infotip to close
                infotip = client.get_window('cardjitsu_snowinfotip.swf')
                infotip.on_close = after_close
                return

            client.send_tip(phase)

    def hide_tip(self, client: "Penguin") -> None:
        client.hide_tip()

    def enable_cards(self) -> None:
        for client in self.clients:
            snow_ui = client.get_window('cardjitsu_snowui.swf')
            snow_ui.send_payload('enableCards')

    def disable_cards(self) -> None:
        for client in self.clients:
            snow_ui = client.get_window('cardjitsu_snowui.swf')
            snow_ui.send_payload('disableCards')

    def update_cards(self) -> None:
        for client in self.clients:
            client.update_cards()

    def unlock_stamp(self, id: int) -> None:
        for client in self.clients:
            client.unlock_stamp(id)

    def display_round_title(self) -> None:
        round_time = ((self.game_start + 300) - time.time()) * 1000

        for client in self.clients:
            round_title = client.get_window('cardjitsu_snowrounds.swf')
            round_title.layer = 'bottomLayer'
            round_title.load(
                {
                    'bonusCriteria': self.bonus_criteria,
                    'remainingTime': max(0, round_time),
                    'roundNumber': self.round
                },
                loadDescription="",
                assetPath="",
                xPercent=0.15,
                yPercent=0.15
            )

        self.wait_for_window('cardjitsu_snowrounds.swf', loaded=True)

    def display_combo_title(self, elements: List[str]) -> None:
        for client in self.clients:
            combo_title = client.get_window('cardjitsu_snowcombos.swf')
            combo_title.layer = 'bottomLayer'
            combo_title.load(
                {'data': elements},
                loadDescription="",
                assetPath="",
                xPercent=0.5,
                yPercent=0.5
            )

        self.wait_for_window(
            'cardjitsu_snowcombos.swf',
            loaded=True,
            timeout=4
        )

    def get_payout_round(self) -> int:
        """Get the round number for the payout screen"""
        if self.round >= 3:
            # Players have entered bonus round
            return 9 - len(self.enemies)

        if not self.enemies and self.round == 2:
            # Players have defeated all enemies
            return 4

        # Players have been defeated
        return self.round + 1

    def display_payout(self) -> None:
        if config.ENABLE_BETA:
            self.display_beta_payout()
            return

        with app.session.database.managed_session() as session:
            snow_stamps = stamps.fetch_all_by_group(60, session=session)

            for client in self.clients:
                if client.disconnected:
                    continue

                if client.object.snow_ninja_rank < 24:
                    required_exp = ExpRequirements.get(client.object.snow_ninja_rank + 1, 3000)
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
                    'snow_ninja_progress': exp_percentage  % 100
                }

                if result_rank >= 13:
                    # Unlock "Snow Pro" stamp
                    client.unlock_stamp(487, session=session)

                if len(self.enemies) <= 0:
                    # Update win count
                    key = f'snow_progress_{client.element}_wins'
                    wins = getattr(client.object, key, 0)
                    updates[key] = wins + 1

                    if updates[key] >= 3:
                        stamp_ids = {
                            'fire': 470,
                            'water': 471,
                            'snow': 469
                        }

                        # Unlock stamp
                        client.unlock_stamp(
                            stamp_ids[client.element],
                            session=session
                        )

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

                # Display payout swf window
                payout = client.get_window('cardjitsu_snowpayout.swf')
                payout.layer = 'bottomLayer'
                payout.load(
                    {
                        "coinsEarned": coins,
                        "doubleCoins": int(double_coins),
                        "damage": 0,
                        "isBoss": 0,
                        "rank": client.object.snow_ninja_rank + 1,
                        "round": self.get_payout_round(),
                        "showItems": 0,
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

    def display_beta_payout(self) -> None:
        with app.session.database.managed_session() as session:
            for client in self.clients:
                if client.disconnected:
                    continue

                # Calculate percentage based on round
                exp_gained = (self.get_payout_round() * 11) + 1
                beta_reward_item = 1600

                if not config.DISABLE_REWARDS:

                    if exp_gained >= 100:
                        # Add item to inventory
                        items.add(
                            client.pid,
                            item_id=beta_reward_item,
                            session=session
                        )

                        self.logger.info(f'{client} unlocked item {beta_reward_item}')

                # Display payout swf window
                payout = client.get_window('cardjitsu_snowpayoutbeta.swf')
                payout.layer = 'bottomLayer'
                payout.load(
                    {
                        "coinsEarned": 0,
                        "doubleCoins": False, # TODO
                        "damage": 0, # Only important for tusk battle
                        "isBoss": 0,
                        "rank": 24,
                        "round": self.get_payout_round(),
                        "showItems": 0, # Only important for tusk battle
                        "stampList": [],
                        "stamps": [],
                        "xpStart": 0,
                        "xpEnd": exp_gained
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
            if ninja.client.disconnected:
                continue

            if ninja.hp <= 0:
                ninja.set_health(1)

            ninja.win_animation()

        time.sleep(3.5)
