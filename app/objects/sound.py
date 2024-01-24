
from ..engine.game import Game
from .asset import Asset

class Sound(Asset):
    handle_id: int
    looping: bool = False
    volume: int = 100
    radius: int = 0
    game_object_id: int = -1
    response_object_id: int = -1

    def play(self, game: Game) -> None:
        game.send_tag(
            'FX_PLAYSOUND',
            f'0:{self.index}',
            self.handle_id,
            int(self.looping),
            self.volume,
            self.game_object_id,
            self.radius,
            self.response_object_id
        )
