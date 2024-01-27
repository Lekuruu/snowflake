
from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple, Iterator
from app.objects import GameObject, Asset
from app.objects.ninjas import Ninja

if TYPE_CHECKING:
    from app.engine.penguin import Penguin
    from app.engine.game import Game

import random

class Grid:
    def __init__(self, game: "Game") -> None:
        self.array: List[List[GameObject | None]] = [[None] * 5 for _ in range(9)]
        self.tiles: List[GameObject] = []
        self.enemy_spawns = [range(6, 9), range(5)]
        self.game = game

        # X, Y offset for ninjas & enemies
        self.x_offset = 0.5
        self.y_offset = 1

    def __repr__(self) -> str:
        return f"<Grid ({self.array})>"

    def __getitem__(self, index: Tuple[int, int]) -> GameObject | None:
        return self.array[index[0]][index[1]]

    def __setitem__(self, index: Tuple[int, int], value: GameObject | None) -> None:
        self.array[index[0]][index[1]] = value

        if value is not None:
            value.x, value.y = index[0], index[1]

    def add(self, obj: GameObject) -> None:
        """Add a game object to the grid"""
        self.__setitem__((obj.x, obj.y), obj)

    def remove(self, obj: GameObject) -> None:
        """Remove a game object from the grid"""
        x, y = self.coordinates(obj)
        self[x, y] = None

    def coordinates(self, obj: GameObject) -> Tuple[int, int]:
        """Get the coordinates of an object"""
        for x in range(9):
            for y in range(5):
                if self[x, y] != obj:
                    continue
                return (x, y)
        return (-1, -1)

    def enemy_spawn_location(self, max_attempts=100) -> Tuple[int, int]:
        """Get a random enemy spawn location"""
        for _ in range(max_attempts):
            x = random.choice(self.enemy_spawns[0])
            y = random.choice(self.enemy_spawns[1])

            if self.can_move(x, y):
                return (x, y)

        return (-1, -1)

    def can_move(self, x: int, y: int) -> bool:
        """Check if a tile is empty"""
        if x not in range(9) or y not in range(5):
            return False

        return self[x, y] is None

    def can_move_to_tile(self, ninja: Ninja, x: int, y: int) -> bool:
        """Check if a ninja can move to a tile"""
        if x not in range(9) or y not in range(5):
            return False

        if not self.can_move(x, y):
            return False

        distance = abs(x - ninja.x) + abs(y - ninja.y)

        return distance <= ninja.move

    def initialize_tiles(self) -> None:
        """Initialize the tiles, and the tile frame"""
        tile_frame = GameObject(self.game, 'ui_tile_frame')
        tile_frame.assets.add(Asset.from_name('ui_tile_frame'))
        tile_frame.assets.add(Asset.from_name('blank_png'))
        tile_frame.place_object()

        for x in range(9):
            for y in range(5):
                tile = GameObject(
                    self.game,
                    f'{x}-{y}',
                    x + 0.5,
                    y + 0.9998,
                    on_click=self.on_tile_click,
                )
                tile.assets.add(Asset.from_name('ui_tile_move'))
                tile.assets.add(Asset.from_name('ui_tile_attack'))
                tile.assets.add(Asset.from_name('ui_tile_heal'))
                tile.assets.add(Asset.from_name('ui_tile_no_move'))
                tile.assets.add(Asset.from_name('blank_png'))
                self.tiles.append(tile)
                tile.place_object()

    def movable_tiles(self, ninja: Ninja) -> Iterator[GameObject]:
        for tile in self.tiles:
            x = int(tile.x - 0.5)
            y = int(tile.y - 0.9998)

            if not self.can_move(x, y):
                continue

            distance = abs(x - ninja.x) + abs(y - ninja.y)

            if distance <= ninja.move:
                yield tile

    def show_tiles(self) -> None:
        tile_frame = self.game.objects.by_name('ui_tile_frame')
        tile_frame.place_sprite('ui_tile_frame')

        for client in self.game.clients:
            ninja = self.game.objects.by_name(client.element.capitalize())

            for tile in self.movable_tiles(ninja):
                tile.place_sprite('ui_tile_move', client)

    def hide_tiles(self) -> None:
        tile_frame = self.game.objects.by_name('ui_tile_frame')
        tile_frame.hide()

        for tile in self.tiles:
            tile.hide()

    def on_tile_click(self, client: "Penguin", tile: GameObject, *args) -> None:
        x = int(tile.x - 0.5)
        y = int(tile.y - 0.9998)

        ninja = self.game.objects.by_name(client.element.capitalize())
        ninja.place_ghost(x, y)
