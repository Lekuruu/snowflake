
from __future__ import annotations
from typing import List

from ..objects.collections import Players
from .penguin import Penguin
from .tusk import TuskGame
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

            if player.battle_mode != 0:
                self.create_tusk_game(*match)
                return

            self.create_normal_game(*match)

        # TODO: Add matchmaking timeout error

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
            matches = self.players.with_element(
                element,
                player.battle_mode
            )

            if not matches:
                continue

            # Sort by closest rank
            players.sort(
                key=lambda other: abs(
                    player.object.snow_ninja_rank -
                    other.object.snow_ninja_rank
                )
            )

            # Add closest match
            players.append(matches[0])

        if len(players) != 3:
            if not config.ENABLE_DEBUG_PLAYERS:
                return

            players = self.get_debug_players(players)

        players.sort(key=lambda x: x.element)
        return players

    def create_normal_game(self, fire: Penguin, snow: Penguin, water: Penguin) -> None:
        game = Game(fire, snow, water)
        game.server.games.add(game)

        for client in game.clients:
            player_select = client.get_window(config.PLAYERSELECT_SWF)
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

    def create_tusk_game(self, fire: Penguin, snow: Penguin, water: Penguin) -> None:
        game = TuskGame(fire, snow, water)
        game.server.games.add(game)

        for client in game.clients:
            player_select = client.get_window(config.PLAYERSELECT_SWF)
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
        battle_mode = players[0].battle_mode

        for player in players:
            elements.remove(player.element)

        for element in elements:
            debug_player = Penguin(player.server, player.address)
            debug_player.pid = -1
            debug_player.name = f'Debug {element.title()} Player'
            debug_player.element = element
            debug_player.battle_mode = battle_mode
            debug_player.in_queue = True
            debug_player.is_ready = True
            debug_player.logged_in = True
            debug_player.disconnected = True
            debug_player.object = player.object
            players.append(debug_player)

        return players
