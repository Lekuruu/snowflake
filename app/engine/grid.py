
from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple, Iterator
from app.objects import GameObject, Asset
from app.objects.ninjas import Ninja
from app.data.constants import TipPhase

if TYPE_CHECKING:
    from app.engine.penguin import Penguin
    from app.engine.game import Game

import random
import math

class Grid:
    def __init__(self, x_range: int, y_range: int, game: "Game") -> None:
        self.array: List[List[GameObject | None]] = [[None] * y_range for _ in range(x_range)]
        self.tiles: List[GameObject] = []
        self.x_range = range(x_range)
        self.y_range = range(y_range)
        self.game = game

    def __repr__(self) -> str:
        return f"<Grid ({self.array})>"

    def __getitem__(self, index: Tuple[int, int]) -> GameObject | None:
        if self.is_valid(*index):
            return self.array[index[0]][index[1]]

    def __setitem__(self, index: Tuple[int, int], value: GameObject | None) -> None:
        if not self.is_valid(*index):
            return

        self.array[index[0]][index[1]] = value

        if value is not None:
            value.x, value.y = index[0], index[1]

    @property
    def obstacles(self) -> List[Tuple[int, int]]:
        """Get all "obstacles" on the grid"""
        return (
            [(obj.x, obj.y) for obj in self.game.rocks]
            # TODO: Should ninjas & enemies be obstacles?
        )

    def add(self, obj: GameObject) -> None:
        """Add a game object to the grid"""
        self.__setitem__((obj.x, obj.y), obj)

    def remove(self, obj: GameObject) -> None:
        """Remove a game object from the grid"""
        x, y = self.coordinates(obj)
        self[x, y] = None

    def move(self, obj: GameObject, x: int, y: int) -> None:
        """Move a game object to a new location"""
        self.remove(obj)
        self[x, y] = obj

    def coordinates(self, obj: GameObject) -> Tuple[int, int]:
        """Get the coordinates of an object"""
        for x in range(9):
            for y in range(5):
                if self[x, y] != obj:
                    continue
                return (x, y)
        return (-1, -1)

    def distance(self, start: Tuple[int, int], target: Tuple[int, int]) -> int:
        """Get the manhatten distance between two tiles"""
        return abs(start[0] - target[0]) + abs(start[1] - target[1])

    def distance_with_obstacles(self, start: Tuple[int, int], target: Tuple[int, int]) -> int | float:
        """Get the Manhattan distance between two tiles, accounting for obstacles"""
        if target in self.obstacles:
            return math.inf

        for obstacle in self.obstacles:
            # Check if the obstacle lies on the line segment between start and target
            if self.is_obstacle_between(start, target, obstacle):
                return math.inf

        distance = self.distance(start, target)
        return distance

    def is_obstacle_between(self, start: Tuple[int, int], target: Tuple[int, int], obstacle: Tuple[int, int]) -> bool:
        """Check if an obstacle lies on the line segment between start and target"""
        x1, y1 = start
        x2, y2 = target
        x3, y3 = obstacle

        # Check if the obstacle is collinear with start and target
        if (x2 - x1) * (y3 - y1) == (x3 - x1) * (y2 - y1):
            # Check if the obstacle lies within the rectangle formed by start and target
            if min(x1, x2) <= x3 <= max(x1, x2) and min(y1, y2) <= y3 <= max(y1, y2):
                return True

        return False

    def enemy_spawn_location(self, max_attempts=100) -> Tuple[int, int]:
        """Get a random enemy spawn location"""
        spawn_range = [range(7, 9), range(5)]

        for _ in range(max_attempts):
            x = random.choice(spawn_range[0])
            y = random.choice(spawn_range[1])

            if self.can_move(x, y):
                return (x, y)

        return (-1, -1)

    def is_valid(self, x: int, y: int) -> bool:
        """Check if a tile is valid"""
        return x in self.x_range and y in self.y_range

    def can_move(self, x: int, y: int) -> bool:
        """Check if a tile is empty"""
        if not self.is_valid(x, y):
            return False

        return self[x, y] is None

    def can_move_to_tile(self, ninja: Ninja, x: int, y: int) -> bool:
        """Check if a ninja can move to a tile"""
        if not self.is_valid(x, y):
            return False

        if not self.can_move(x, y):
            return False

        distance = abs(x - ninja.x) + abs(y - ninja.y)

        return distance <= ninja.move

    def initialize_tiles(self) -> None:
        """Initialize the tiles, and the tile frame"""
        tile_frame = GameObject(self.game, 'ui_tile_frame')
        tile_frame.place_object()

        for x in self.x_range:
            for y in self.y_range:
                tile = GameObject(
                    self.game,
                    f'{x}-{y}',
                    x,
                    y,
                    on_click=self.on_tile_click,
                    x_offset=0.5,
                    y_offset=0.9998
                )
                self.tiles.append(tile)
                tile.place_object()

    def show_tiles(self) -> None:
        """Show all initialized tiles, including the tile frame"""
        tile_frame = self.game.objects.by_name('ui_tile_frame')
        tile_frame.place_sprite('ui_tile_frame')

        for client in self.game.clients:
            if client.ninja.hp <= 0:
                continue

            for tile in client.ninja.movable_tiles():
                tile.place_sprite('ui_tile_move', client)

    def hide_tiles(self) -> None:
        """Hide all initialized tiles, including the tile frame"""
        tile_frame = self.game.objects.by_name('ui_tile_frame')
        tile_frame.hide()

        for tile in self.tiles:
            tile.hide()

    def place_tile(self, x: int, y: int, sprite: str = 'ui_tile_move') -> None:
        """Place a tile at a specific location"""
        tile = self.get_tile(x, y)
        tile.place_sprite(sprite)

    def change_tiles(self, name: str) -> None:
        """Change the sprites of all tiles to a new sprite"""
        for client in self.game.clients:
            for tile in client.ninja.movable_tiles():
                tile.place_sprite(name, client)

    def change_tiles_for_client(self, client: "Penguin", name: str, ghost=False, ignore_objects=False) -> None:
        """Change the sprites of all tiles to a new sprite for a specific client"""
        if not ignore_objects:
            tiles = client.ninja.movable_tiles() if not ghost else \
                    client.ninja.movable_ghost_tiles()

            for tile in tiles:
                tile.place_sprite(name, client)

            if client.ninja.placed_ghost:
                ghost_tile = self.get_tile(client.ninja.ghost.x, client.ninja.ghost.y)
                ghost_tile.place_sprite(name, client)

        else:
            tiles = client.ninja.tiles_in_range() if not ghost else \
                    client.ninja.ghost_tiles_in_range()

            for tile in tiles:
                tile.place_sprite(name, client)

    def hide_tiles_for_client(self, client: "Penguin") -> None:
        """Hide all tiles for a specific client"""
        for tile in self.tiles:
            tile.hide(client)

    def get_tile(self, x: int, y: int) -> GameObject | None:
        """Get a tile by its coordinates"""
        return next((tile for tile in self.tiles if tile.x == x and tile.y == y), None)

    def on_tile_click(self, client: "Penguin", tile: GameObject, *args) -> None:
        if client.selected_card:
            client.ninja.place_powercard(tile.x, tile.y)
            return

        ninja = self.game.objects.by_name(client.element.capitalize())
        ninja.place_ghost(tile.x, tile.y)

        if client.tip_mode and client.last_tip == TipPhase.MOVE:
            client.game.hide_tip(client)

    def surrounding_tiles(self, center_x: int, center_y: int, distance: int = 1) -> Iterator[GameObject]:
        """Get the surrounding tiles of a tile, in a rectangle-like pattern"""
        x_range = range(center_x - distance, center_x + distance + 1)
        y_range = range(center_y - distance, center_y + distance + 1)

        for x in x_range:
            for y in y_range:
                if not self.is_valid(x, y):
                    continue

                if x == center_x and y == center_y:
                    continue

                yield self.get_tile(x, y)

    def surrounding_objects(self, x: int, y: int, distance: int = 1) -> Iterator[GameObject]:
        """Get the surrounding objects of a tile, in a rectangle-like pattern"""
        tiles = self.surrounding_tiles(x, y, distance)

        for tile in tiles:
            if (object := self[tile.x, tile.y]) is not None:
                yield object
