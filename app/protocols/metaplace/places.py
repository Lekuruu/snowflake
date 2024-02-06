
from dataclasses import dataclass
from app.data import ViewMode

@dataclass
class MapBlocks:
    tilemap: str = ""
    heightmap: str = ""

@dataclass
class ZoomLimit:
    x: int = -1
    y: int = -1

@dataclass
class Render:
    alpha_cutoff: int = 48
    occlude_tiles: bool = False

@dataclass
class Camera:
    view_mode: ViewMode = ViewMode.SIDE
    lock_view: bool = False
    lock_zoom: bool = False
    tile_size: int = 64
    elevation_scale: float = -1
    terrain_lighting: bool = True

    lock_scroll: bool = True
    move_radius: int = 0
    move_rate: int = 0
    move_recenter: int = 0

    height_map_divisions: int = 1
    height_map_scale: float = 0.5

    margin_top_left_x: int = 0
    margin_top_left_y: int = 0
    margin_bottom_right_x: int = 0
    margin_bottom_right_y: int = 0

@dataclass
class Camera3D:
    near: int = 0
    far: int = 0
    position: tuple = (0, 0, 0)
    angle: tuple = (0, 0, 0)
    camera_view: int = 0
    left: int = 0
    right: int = 0
    top: int = 0
    bottom: int = 0
    aspect: int = 0
    v_fov: int = 0
    focal_length: int = 864397819904
    unknown: int = 0
    camera_width: int = 1024
    camera_height: int = 768

@dataclass
class Physics:
    gravity: bool = False
    collision: bool = False
    friction: bool = False
    tile_friction: bool = False
    safety_net: bool = False
    net_height: int = 0
    net_friction: bool = False
    net_bounce: bool = True

@dataclass
class Place:
    id: int = 0
    name: str = ""
    mapblocks: MapBlocks = MapBlocks()
    zoom_limit: ZoomLimit = ZoomLimit()
    render: Render = Render()
    camera: Camera = Camera()
    camera3d: Camera3D = Camera3D()
    physics: Physics = Physics()
    draggable: bool = False
    object_lock: bool = False
