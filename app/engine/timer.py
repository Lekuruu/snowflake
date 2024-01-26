
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import Game

import time

class Timer:
    def __init__(self, game: "Game") -> None:
        self.game = game
        self.tick = 10
        self.loaded = False

    def run(self) -> None:
        if not self.loaded:
            self.load()
            self.loaded = True

        self.show()
        while self.tick > 0:
            time.sleep(1)
            self.tick -= 1
            self.update()

        self.hide()
        self.tick = 10

    def load(self) -> None:
        for client in self.game.clients:
            timer = client.window_manager.get_window('cardjitsu_snowtimer.swf')
            timer.layer = 'bottomLayer'
            timer.load(
                {'element': client.element},
                loadDescription="",
                assetPath="",
                xPercent=0.5,
                yPercent=0
            )

    def update(self) -> None:
        for client in self.game.clients:
            timer = client.window_manager.get_window('cardjitsu_snowtimer.swf')
            timer.send_payload(
                'update',
                {'tick': self.tick}
            )

    def show(self) -> None:
        for client in self.game.clients:
            timer = client.window_manager.get_window('cardjitsu_snowtimer.swf')
            timer.send_payload('Timer_Start')
            timer.send_payload('enableConfirm')

    def hide(self) -> None:
        for client in self.game.clients:
            timer = client.window_manager.get_window('cardjitsu_snowtimer.swf')
            timer.send_payload('skipToTransitionOut')
            timer.send_payload('disableConfirm')
