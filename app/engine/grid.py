
from __future__ import annotations

from app.objects import GameObject
from typing import List, Tuple

import random

class Grid:
    def __init__(self) -> None:
        self.array: List[List[GameObject | None]] = [[None] * 5 for _ in range(9)]
        self.x_offset = 0.5
        self.y_offset = 1
        self.enemy_spawns = [range(6, 9), range(5)]

    def __repr__(self) -> str:
        return f"<Grid ({self.array})>"

    def __getitem__(self, index: Tuple[int, int]) -> GameObject | None:
        return self.array[index[0]][index[1]]

    def __setitem__(self, index: Tuple[int, int], value: GameObject | None) -> None:
        self.array[index[0]][index[1]] = value

        if value is not None:
            value.x, value.y = index[0] + self.x_offset, index[1] + self.y_offset


    def can_move(self, x: int, y: int) -> bool:
        if x not in range(9) or y not in range(5):
            return False

        return self[x, y] is None

    def coordinates(self, obj: GameObject) -> Tuple[int, int]:
        for x in range(9):
            for y in range(5):
                if self[x, y] != obj:
                    continue
                return (x, y)
        return (-1, -1)

    def game_coordinates(self, obj: GameObject) -> Tuple[int, int]:
        x, y = self.coordinates(obj)
        return (
            x + self.x_offset,
            y + self.y_offset
        )

    def enemy_spawn_location(self) -> Tuple[int, int]:
        x, y = -1, -1

        while not self.can_move(x, y):
            x = random.choice(self.enemy_spawns[0])
            y = random.choice(self.enemy_spawns[1])

        return (x, y)
