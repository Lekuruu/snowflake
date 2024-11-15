
from __future__ import annotations
from typing import Tuple, List, TYPE_CHECKING

from app.data import Card, TipPhase
from app.objects import GameObject, LocalGameObject
from app.objects.enemies import Enemy
from app.objects.ninjas import Ninja
from app.objects.effects import (
    WaterPowerBeam,
    FirePowerBeam,
    SnowPowerBeam,
    MemberReviveBeam,
    FirePowerBottle,
    WaterFishDrop,
    SnowIgloo,
    Explosion,
    Shield,
    Flame,
    Rage
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
            x=-1,
            y=-1,
            x_offset=0.5,
            y_offset=1.015
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

    @property
    def targets(self) -> List[GameObject]:
        return set(self.game.grid.objects_in_range(
            *self.pattern_range(self.x, self.y)
        ))

    @property
    def element_name(self) -> str:
        return {
            'f': 'fire',
            'w': 'water',
            's': 'snow'
        }.get(self.element)

    @property
    def card_data(self) -> dict:
        return {
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

    def place(self, x: int, y: int) -> None:
        self.place_card_sprite(x, y)
        self.place_pattern_sprite(x, y)

        if self.client.tip_mode and self.client.last_tip == TipPhase.CARD:
            self.client.hide_tip()

        self.object.play_sound('sfx_mg_2013_cjsnow_uiselecttile', self.client)

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

    def use(self, is_combo=False) -> None:
        if self.client.ninja.hp <= 0:
            return

        if self.client.selected_card != self:
            return

        if self.x == -1 and self.y == -1:
            return

        # Play card animation
        self.consume()

        # Wait for client to consume card
        self.game.callbacks.wait_for_client(
            'ConsumeCardResponse',
            client=self.client,
            timeout=2
        )

        # Wait for card animation
        time.sleep(1.2)

        self.attack_animation()
        self.apply_health()

        if is_combo:
            self.apply_effects()

        self.client.played_cards += 1
        self.check_stamps(is_combo)
        self.game.wait_for_animations()

    def consume(self) -> None:
        for client in self.game.clients:
            payload_name = 'consumeCard'
            data = {}

            if self.client != client:
                payload_name = 'showCaseOthersCard'
                data["cardData"] = self.card_data

            snow_ui = client.get_window('cardjitsu_snowui.swf')
            snow_ui.send_payload(payload_name, data)

    def attack_animation(self) -> None:
        self.client.ninja.power_animation()

        beam_class = {
            'fire': FirePowerBeam,
            'water': WaterPowerBeam,
            'snow': SnowPowerBeam
        }[self.element_name]

        beam = beam_class(self.game, self.client.ninja.x, self.client.ninja.y)
        beam.play()

        impact_class = {
            'fire': FirePowerBottle,
            'water': WaterFishDrop,
            'snow': SnowIgloo
        }[self.element_name]

        if self.element != 's':
            # Wait for attack animation
            time.sleep(0.2)

        impact = impact_class(self.game, self.x, self.y)
        impact.play()

        if self.element == 'f':
            time.sleep(impact.duration)
            impact.remove_object()
            time.sleep(beam.duration - impact.duration)
            beam.remove_object()
            return

        beam_delay = 0.85
        time.sleep(impact.duration - beam_delay)
        beam.remove_object()
        time.sleep(beam_delay)
        impact.remove_object()

    def apply_health(self) -> None:
        for target in self.targets:
            if isinstance(target, Ninja) and self.element == 's':
                if target.client.disconnected:
                    continue

                target.set_health(target.hp + self.value)
                continue

            if isinstance(target, Enemy):
                attack = self.value

                if self.element == 'w':
                    attack = self.value * 2

                if self.element == 'f':
                    target.stunned = True

                target.set_health(target.hp - attack, wait=False)
                Explosion(self.game, target.x, target.y).play()

    def apply_effects(self) -> None:
        if self.element == 's':
            # Apply shield to all ninjas
            for ninja in self.game.ninjas:
                if ninja.client.disconnected:
                    continue

                if ninja.hp <= 0:
                    continue

                if ninja.shield is not None:
                    continue

                ninja.shield = Shield(self.game, ninja.x, ninja.y)
                ninja.shield.play()

        elif self.element == 'w':
            # Apply rage to all ninjas
            for ninja in self.game.ninjas:
                if ninja.client.disconnected:
                    continue

                if ninja.hp <= 0:
                    continue

                if ninja.rage is not None:
                    continue

                ninja.rage = Rage(self.game, ninja.x, ninja.y)
                ninja.rage.play()

        elif self.element == 'f':
            # Apply flame to all ninjas in targets
            for target in self.targets:
                if not isinstance(target, Enemy):
                    continue

                if target.hp <= 0:
                    continue

                if target.flame is not None:
                    continue

                target.flame = Flame(self.game, target.x, target.y)
                target.flame.play()

    def check_stamps(self, is_combo: bool) -> None:
        ninja_targets = [
            target for target in self.targets
            if isinstance(target, Ninja)
            and not target.client.disconnected
        ]

        if self.client.played_cards >= 3:
            # Unlock "Power Card Pro" stamp
            self.client.unlock_stamp(484)

        if len(ninja_targets) >= 3 and self.element == 's':
            # Unlock "Huge Heal" stamp
            self.client.unlock_stamp(478)
        
        if ninja_targets and is_combo and self.element == 'w':
            # Unlock "Wave Boost" stamp
            self.client.unlock_stamp(481)

        if ninja_targets and is_combo and self.element == 's':
            # Unlock "Snow Shield" stamp
            self.client.unlock_stamp(479)

        enemy_targets = [
            target for target in self.targets
            if isinstance(target, Enemy)
        ]

        if len(enemy_targets) >= 3 and self.element == 'w':
            # Unlock "Tidal Wave" stamp
            self.client.unlock_stamp(480)

        if len(enemy_targets) >= 3 and self.element == 'f':
            # Unlock "Fire Blast" stamp
            self.client.unlock_stamp(482)

            if is_combo:
                # Unlock "Fire Blast Combo" stamp
                self.client.unlock_stamp(483)

class MemberCard(GameObject):
    def __init__(self, client: "Penguin") -> None:
        super().__init__(
            client.game,
            'ui_card_member',
            x=-1,
            y=-1,
            x_offset=0.5,
            y_offset=1.01
        )
        self.selected = False
        self.client = client

    @property
    def element_name(self) -> str:
        return self.client.element

    def place(self) -> None:
        if self.client.ninja.placed_ghost:
            self.x = self.client.ninja.ghost.x
            self.y = self.client.ninja.ghost.y
        else:
            self.x = self.client.ninja.x
            self.y = self.client.ninja.y

        self.place_object()

        sprite_name = {
            'fire': 'ui_card_member_fire',
            'water': 'ui_card_member_water',
            'snow': 'ui_card_member_snow'
        }[self.element_name]

        self.place_sprite(sprite_name)
        self.selected = True

    def remove(self) -> None:
        self.remove_object()
        self.x = -1
        self.y = -1

    def consume(self) -> None:
        if not self.selected:
            return

        for client in self.game.clients:
            payload_name = 'consumeMemberCard'

            if self.client != client:
                payload_name = 'showCaseMemberCard'

            snow_ui = client.get_window('cardjitsu_snowui.swf')
            snow_ui.send_payload(payload_name)

        # Wait for card animation
        time.sleep(2)

        beam = MemberReviveBeam(self.game, self.client.ninja.x, self.client.ninja.y)
        beam.play()

        self.client.ninja.play_sound('SFX_MG_CJSnow_PowercardReviveStart')
        self.client.ninja.set_health(self.client.ninja.max_hp)
        self.client.ninja.revive_membercard_animation()
        self.client.member_card = None

        time.sleep(1.2)
        self.client.ninja.play_sound('SFX_MG_CJSnow_PowercardReviveEnd')
        beam.remove_object()
