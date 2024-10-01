
from typing import TYPE_CHECKING
from app.data import TipPhase

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

        self.running = True
        self.show()

        while self.tick > 0:
            self.update_tick()

        self.running = False
        self.tick = 10
        self.hide()

    def update_tick(self, seconds: int = 1, interval: int = 0.25) -> None:
        while seconds > 0:
            time.sleep(interval)
            seconds -= interval

            if self.game.server.shutting_down:
                self.game.close()
                return

            if all(client.disconnected for client in self.game.clients if not client.is_bot):
                self.game.close()
                return

            if all(client.is_ready for client in self.game.clients if not client.disconnected):
                self.tick = 0
                return

            if self.tick == 3:
                for client in self.game.clients:
                    if client.is_ready:
                        continue

                    self.game.send_tip(TipPhase.CONFIRM, client)

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

        self.game.wait_for_window('cardjitsu_snowtimer.swf', loaded=True)

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
