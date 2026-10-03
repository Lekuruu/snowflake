
from typing import TYPE_CHECKING
from app.data import TipPhase
from .utils import delay

if TYPE_CHECKING:
    from .game import Game

class Timer:
    def __init__(self, game: "Game") -> None:
        self.game = game
        self.tick = 10
        self.loaded = False
        self.running = False

    async def run(self) -> None:
        if not self.loaded:
            await self.load()
            self.loaded = True

        self.running = True
        self.show()

        while self.tick > 0:
            await self.update_tick()

        self.running = False
        self.tick = 10
        self.hide()

    async def update_tick(self, seconds: int | float = 1, interval: float = 0.25) -> None:
        while seconds > 0:
            await delay(interval)
            seconds -= interval

            if self.check_close():
                return

            ready = all(
                # Check ready state only for ninjas with hp > 0
                client.is_ready for client in self.game.clients
                if not client.disconnected and client.ninja.hp > 0
            )

            if ready:
                self.tick = 0
                return

            if self.tick == 3:
                for client in self.game.clients:
                    if client.disconnected:
                        continue

                    if client.is_ready:
                        continue

                    if client.ninja.hp <= 0:
                        continue

                    self.game.send_tip(TipPhase.CONFIRM, client)

        self.tick -= 1
        self.update()

    async def load(self) -> None:
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

        await self.game.wait_for_window('cardjitsu_snowtimer.swf', loaded=True)

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

            if client.ninja.hp > 0:
                # KO'd ninjas apparently can't use confirm
                # https://youtu.be/OP8owGrePTg?t=496
                timer.send_payload('enableConfirm')

    def hide(self) -> None:
        for client in self.game.clients:
            timer = client.get_window('cardjitsu_snowtimer.swf')
            timer.send_payload('skipToTransitionOut')
            timer.send_payload('disableConfirm')

    def check_close(self) -> bool:
        if self.game.server.shutting_down:
            self.game.close()
            return True

        if all(client.disconnected for client in self.game.clients):
            self.game.close()
            return True

        return False
