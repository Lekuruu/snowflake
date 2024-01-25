
from __future__ import annotations

from app.objects import GameObject
from typing import List, Tuple

class Grid:
    def __init__(self) -> None:
        self.array: List[GameObject | None] = [[None]*5]*9
        self.x_offset = 0.5
        self.y_offset = 1

    def __repr__(self) -> str:
        return f"<Grid ({self.array})>"

    def __getitem__(self, index: tuple[int, int]) -> GameObject | None:
        return self.array[index[0]][index[1]]

    def __setitem__(self, index: tuple[int, int], value: GameObject | None) -> None:
        self.array[index[0]][index[1]] = value
        value.x, value.y = index[0] + self.x_offset, index[1] + self.y_offset

    def can_move(self, x: int, y: int) -> bool:
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
