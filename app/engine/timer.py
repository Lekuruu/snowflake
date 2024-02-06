
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import Game

import time

class Timer:
    def __init__(self, game: "Game") -> None:
        self.game = game
        self.tick = 10
        self.loaded = False
        self.running = False

    def run(self) -> None:
        if not self.loaded:
            self.load()
            self.loaded = True

        self.show()
        self.running = True

        while self.tick > 0:
            self.update_tick()

        self.hide()
        self.tick = 10
        self.running = False

    def update_tick(self, seconds: int = 1, interval: int = 0.25) -> None:
        while seconds > 0:
            time.sleep(interval)
            seconds -= interval

            if self.game.server.shutting_down:
                self.game.close()
                return

            if all(client.disconnected for client in self.game.clients):
                self.game.close()
                return

            if all(client.is_ready for client in self.game.clients if not client.disconnected):
                self.tick = 0
                return

        self.tick -= 1
        self.update()

    def load(self) -> None:
        for client in self.game.clients:
            timer = client.get_window('cardjitsu_snowtimer.swf')
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
            timer = client.get_window('cardjitsu_snowtimer.swf')
            timer.send_payload(
                'update',
                {'tick': self.tick}
            )

    def show(self) -> None:
        for client in self.game.clients:
            timer = client.get_window('cardjitsu_snowtimer.swf')
            timer.send_payload('Timer_Start')
            timer.send_payload('enableConfirm')

    def hide(self) -> None:
        for client in self.game.clients:
            timer = client.get_window('cardjitsu_snowtimer.swf')
            timer.send_payload('skipToTransitionOut')
            timer.send_payload('disableConfirm')
