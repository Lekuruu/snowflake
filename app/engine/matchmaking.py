
from __future__ import annotations

from typing import Tuple

from .collections import Players
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
            if (match := self.players.with_element(element)):
                # TODO: Sort players by different criteria
                players.append(match[0])

        if len(players) != 3:
            return

        players.sort(key=lambda x: x.element)
        return players

    def create_game(self, fire: Penguin, snow: Penguin, water: Penguin) -> None:
        self.logger.info('Creating game...')

        fire.in_queue = False
        snow.in_queue = False
        water.in_queue = False

        # TODO: Create game
