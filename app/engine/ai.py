
from __future__ import annotations
from typing import Callable

from twisted.internet.address import IPv4Address
from twisted.internet import reactor

from app.engine.penguin import Penguin
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
        if self.ninja.hp <= 0:
            if not self.member_card:
                self.confirm_move()
                return

            self.member_card.place()
            self.confirm_move()
            return

        # TODO: Moving, Attacking, Powercards
        self.confirm_move()
