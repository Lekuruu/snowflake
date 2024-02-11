
from __future__ import annotations
from typing import List

from ..objects.collections import Players
from .penguin import Penguin
from .game import Game

import logging
import config

class MatchmakingQueue:
    def __init__(self) -> None:
        self.players = Players()
        self.logger = logging.getLogger('Matchmaking')

    def add(self, player: Penguin) -> None:
        self.players.add(player)

        player.logger.info(f'Joined matchmaking queue with "{player.element}"')
        player.in_queue = True

        if (match := self.find_match(player)):
            self.logger.info(f'Found match: {match}')
            self.create_game(*match)

        # TODO: Add matchmakuing timeout error

    def remove(self, player: Penguin) -> None:
        if player in self.players:
            self.players.remove(player)

            player.logger.info('Left matchmaking queue')
            player.in_queue = False

    def find_match(self, player: Penguin) -> List[Penguin] | None:
        elements = ['snow', 'water', 'fire']
        elements.remove(player.element)

        players = [player]

        for element in elements:
            if (matches := self.players.with_element(element)):
                # TODO: Sort players by different criteria
                players.append(matches[0])

        if len(players) != 3:
            if not config.ENABLE_DEBUG_PLAYERS:
                return

            players = self.get_debug_players(players)

        players.sort(key=lambda x: x.element)
        return players

    def create_game(self, fire: Penguin, snow: Penguin, water: Penguin) -> None:
        self.logger.info('Creating game...')

        game = Game(fire, snow, water)
        game.server.games.add(game)

        for client in game.clients:
            player_select = client.get_window('cardjitsu_snowplayerselect.swf')
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
        game.server.runThread(game.start)

    def get_debug_players(self, players: List[Penguin]) -> List[Penguin]:
        elements = ['snow', 'water', 'fire']

        for player in players:
            elements.remove(player.element)

        for element in elements:
            debug_player = Penguin(player.server, player.address)
            debug_player.pid = -1
            debug_player.name = f'Debug {element.title()} Player'
            debug_player.element = element
            debug_player.in_queue = True
            debug_player.is_ready = True
            debug_player.logged_in = True
            debug_player.disconnected = True
            debug_player.object = player.object
            players.append(debug_player)

        return players
