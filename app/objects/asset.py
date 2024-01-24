
from dataclasses import dataclass

@dataclass
class Asset:
    index: int
    name: str
    url: str

    def __eq__(self, asset: "Asset") -> bool:
        return self.index == asset.index

    def __hash__(self) -> int:
        return hash(self.index)
