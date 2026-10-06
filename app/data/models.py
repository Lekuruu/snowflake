
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class PenguinData:
    """The player data required by snowflake"""

    id: int
    nickname: str
    approval_en: bool
    rejection_en: bool
    snow_ninja_rank: int
    snow_ninja_progress: int
    coins: int
    snow_progress_fire_wins: int = 0
    snow_progress_water_wins: int = 0
    snow_progress_snow_wins: int = 0

@dataclass
class CardData:
    """A card-jitsu card"""

    id: int = 0
    name: str = ""
    set_id: int = 0
    power_id: int = 0
    element: str = "s"
    color: str = "b"
    value: int = 0
    description: str = ""

@dataclass
class StampData:
    """Stamp data used by the game & payout screens"""

    id: int
    name: str
    group_id: int
    member: bool
    rank: int
    description: str = ""

@dataclass
class PowerCardCounts:
    fire: int = 0
    water: int = 0
    snow: int = 0
