
from __future__ import annotations
from typing import Callable

from twisted.internet.address import IPv4Address
from twisted.internet import reactor

from app.engine.penguin import Penguin
from app.objects.ninjas import Ninja
from app.objects import GameObject
from app.data import penguins

import random

def delay(min: int, max: int) -> Callable:
    def decorator(func: Callable) -> Callable:
        return lambda *args, **kwargs: reactor.callLater(
            random.uniform(min, max),
            func, *args, **kwargs
        )
    return decorator

class PenguinAI(Penguin):
    def __init__(
        self,
        server,
        element: str,
        battle_mode: int
    ) -> None:
        super().__init__(server, IPv4Address('TCP', '127.0.0.1', 69420))
        self.object = penguins.fetch_random()
        self.name = self.object.nickname
        self.element = element
        self.battle_mode = battle_mode
        self.pid = -1
        self.in_queue = True
        self.is_ready = True
        self.logged_in = True
        self.is_bot = True

    @delay(0.25, 1.5)
    def confirm_move(self) -> None:
        if self.is_ready:
            return

        confirm = GameObject(
            self.game,
            'ui_confirm',
            x_offset=0.5,
            y_offset=1.05
        )

        confirm.x = self.ninja.x
        confirm.y = self.ninja.y
        confirm.place_object()
        confirm.place_sprite(confirm.name)
        confirm.play_sound('SFX_MG_2013_CJSnow_UIPlayerReady_VBR8')
        self.is_ready = True

    @delay(0.5, 3)
    def select_move(self) -> None:
        # Check for k.o. state
        if self.ninja.hp <= 0:
            if not self.member_card:
                self.confirm_move()
                return

            self.member_card.place()
            self.confirm_move()
            return

        # Check for k.o. allies
        for ninja in self.game.ninjas:
            if not ninja.hp <= 0:
                continue

            # if ninja.client.member_card:
            #     continue

            if self.is_ninja_getting_revived(ninja):
                continue

            if not self.can_heal_ninja(ninja):
                continue

            self.select_target(ninja.x, ninja.y)
            self.confirm_move()
            return

        actions = {
            'snow': self.snow_actions,
            'water': self.water_actions,
            'fire': self.fire_actions
        }

        actions[self.element]()
        self.confirm_move()

    def select_target(self, x: int, y: int) -> None:
        target = next(
            (target for target in self.ninja.targets
            if target.x == x and target.y == y),
            None
        )

        if not target:
            return

        target.select()

    def snow_actions(self) -> None:
        # Snow should keep a distance from all enemies
        # and focus on healing their allies
        ...

    def fire_actions(self) -> None:
        # Fire should keep a distance from all enemies
        # and focus on attacking their enemies
        ...

    def water_actions(self) -> None:
        # Water needs to move as close as possible to their
        # enemies and focus on attacking them
        ...

    def is_ninja_getting_revived(self, ninja: Ninja) -> bool:
        for ninja in self.game.ninjas:
            if ninja.selected_object == ninja:
                return True

        return False

    def can_heal_ninja(self, target: Ninja) -> bool:
        tiles = self.game.grid.surrounding_tiles(
            target.x,
            target.y
        )

        for tile in tiles:
            can_move = self.game.grid.can_move_to_tile(
                self.ninja,
                tile.x,
                tile.y
            )

            if not can_move:
                continue

            self.ninja.place_ghost(tile.x, tile.y)
            return True

        current_tile = self.game.grid[self.ninja.x, self.ninja.y]

        if current_tile in tiles:
            return True

        return False

    def unlock_stamp(self, id, session) -> None:
        # Bots don't have an account for stamps
        pass
