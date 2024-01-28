
from __future__ import annotations

from twisted.internet import threads
from typing import Tuple

from ..data.repositories import penguins
from ..objects.collections import Players
from .penguin import Penguin

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
                players.append(matches[0])
                # TODO: Sort players by different criteria

        if len(players) != 3:
            return

        players.sort(key=lambda x: x.element)
        return players

    def create_game(self, fire: Penguin, snow: Penguin, water: Penguin) -> None:
        from .game import Game

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
        threads.deferToThread(game.start) \
               .addErrback(game.error_callback)
