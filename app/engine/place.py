from app.protocols.metaplace.places import Place, MapBlocks, Camera
from dataclasses import dataclass

@dataclass
class SnowMapBlocks(MapBlocks):
    tilemap: str = "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAFCAAAAACyOJm3AAAADklEQVQImWNghgEGIlkADWEAiDEh28IAAAAASUVORK5CYII="
    heightmap: str = "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAGCAAAAADfm1AaAAAADklEQVQImWOohwMG8pgA1rMdxRJRFewAAAAASUVORK5CYII="

@dataclass
class SnowCamera(Camera):
    position: tuple = (4.5, 2.5, 0)
    lock_zoom: bool = True
    lock_view: bool = True
    zoom: float = 1.0
    tile_size: int = 100
    elevation_scale: float = 0.031250

@dataclass
class SnowLobby(Place):
    id: int = 0
    name: str = "snow_lobby"
    mapblocks = SnowMapBlocks()
    camera = SnowCamera()

@dataclass
class SnowBattle(SnowLobby):
    id: int = 10001
    name: str = "snow_battle"
