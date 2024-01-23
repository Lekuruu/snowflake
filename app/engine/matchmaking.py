
from __future__ import annotations

from typing import Tuple

from .collections import Players
from .penguin import Penguin
from .game import Game

import threading
import logging

class MatchmakingQueue:
    def __init__(self) -> None:
        self.players = Players()
        self.logger = logging.getLogger('matchmaking')

    def add(self, player: Penguin) -> None:
        self.players.add(player)

        player.logger.info(f'Joined matchmaking queue with "{player.element}"')
        player.in_queue = True

        if (match := self.find_match(player)):
            player.is_host = True
            self.logger.info(f'Found match: {match}')
            self.create_game(*match)

    def remove(self, player: Penguin) -> None:
        if player in self.players:
            self.players.remove(player)

            player.logger.info('Left matchmaking queue')
            player.in_queue = False

    def find_match(self, player: Penguin) -> Tuple[Penguin] | None:
        elements = ['snow', 'water', 'fire']
        elements.remove(player.element)

        players = [player]

        for element in elements:
            if (matches := self.players.with_element(element)):
                # TODO: Sort players by different criteria
                players.append(matches[0])

        if len(players) != 3:
            return

        players.sort(key=lambda x: x.element)
        return players

    def create_game(self, fire: Penguin, snow: Penguin, water: Penguin) -> None:
        self.logger.info('Creating game...')

        fire.in_queue = False
        snow.in_queue = False
        water.in_queue = False

        game = Game(fire, snow, water)

        for client in game.clients:
            player_select = client.window_manager.get_window('cardjitsu_snowplayerselect.swf')
            player_select.send_payload(
                'matchFound',
                {
                    1: fire.name,
                    2: water.name,
                    4: snow.name
                }
            )

            # Remove from matchmaking queue
            self.remove(client)

        # Start game loop
        threading.Thread(
            target=game.start,
            daemon=True
        ).start()
        # TODO: Refactor thread creation
