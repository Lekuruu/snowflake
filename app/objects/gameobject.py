
from dataclasses import dataclass
from .asset import Asset

@dataclass
class GameObject:
    id: int
    name: str
    asset: Asset
    x: int
    y: int
