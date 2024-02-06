
from __future__ import annotations

from twisted.internet.address import IPv4Address, IPv6Address
from twisted.protocols.basic import LineOnlyReceiver
from twisted.python.failure import Failure
from typing import List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from app.protocols import MetaplaceWorldServer

from app.protocols.metaplace.places import Place, Camera3D
from app.engine.windows import WindowManager
from app.objects import ObjectCollection
from app.data import (
    MapblockType,
    AlignMode,
    ScaleMode,
    ViewMode
)

import logging
import time
import json
import ast

class MetaplaceProtocol(LineOnlyReceiver):
    def __init__(self, server: "MetaplaceWorldServer", address: IPv4Address | IPv6Address):
        self.address = address
        self.server = server

        self.pid: int = 0
        self.name: str = ""
        self.token: str = ""
        self.logged_in: bool = False
        self.disconnected: bool = False
        self.place: Place | None = None

        self.last_action = time.time()
        self.logger = logging.getLogger(address.host)

        self.window_manager = WindowManager(self)
        self.local_objects = ObjectCollection()

    def dataReceived(self, data: bytes):
        # NOTE: The socket policy file usually gets requested on a seperate server
        #       This is just used as a fallback, in case the policy file server is down
        if data.startswith(b'<policy-file-request/>'):
            self.logger.debug(f'-> "{data.decode()}"')
            self.sendLine(self.server.policy_file.encode())
            self.close_connection()
            return

        return super().dataReceived(data)

    def lineReceived(self, line: bytes) -> None:
        self.last_action = time.time()

        try:
            data = line.decode("utf-8")
        except UnicodeDecodeError:
            self.logger.warning(f'Invalid request: "{line}"')
            self.close_connection()
            return

        try:
            parsed = data.split(' ')
            command, args = parsed[0], parsed[1:]
        except (ValueError, UnicodeDecodeError):
            self.logger.warning(f'Invalid request: "{data}"')
            self.close_connection()
            return

        for index, argument in enumerate(args):
            try:
                if argument.startswith('{'):
                    # We received a json string
                    args = [json.loads(' '.join(args))]
                    break

                # Try to convert the argument to a Python object
                args[index] = ast.literal_eval(argument)
            except (ValueError, SyntaxError, json.JSONDecodeError):
                pass

        self.command_received(command, args)

    def connectionLost(self, reason: Failure | None = None) -> None:
        if reason is not None and not self.disconnected:
            self.logger.warning(f"Connection lost: {reason.getErrorMessage()}")

        self.server.players.remove(self)
        self.disconnected = True

    def close_connection(self) -> None:
        if not self.transport:
            return

        self.transport.loseConnection()
        self.connectionLost()

    def send_tag(self, tag: str, *args) -> None:
        if not self.transport:
            return

        self.logger.debug(f'<- "{tag}": {args}')

        encoded_arguments = '|'.join(str(a) for a in args)
        self.sendLine((f'[{tag}]|{encoded_arguments}|').encode())

    def get_window(self, name: str | None = None, url: str | None = None):
        return self.window_manager.get_window(name, url)

    def load_window(self, name: str, initial_payload: dict = None, **kwargs) -> None:
        return self.window_manager.get_window(name).load(initial_payload, **kwargs)

    def send_login_reply(self):
        self.send_tag('S_LOGIN', self.pid)

    def send_login_message(self, message: str):
        self.send_tag('S_LOGINDEBUG', message)

    def send_login_error(self, code: int = 900):
        self.send_tag('S_LOGINDEBUG', f'user code {code}')

    def align_ui(self, x: int, y: int, align: AlignMode, scale: ScaleMode):
        self.send_tag('UI_ALIGN', self.server.world_id, x, y, align.value, scale.value)

    def set_background_color(self, r: int, g: int, b: int):
        self.send_tag('UI_BGCOLOR', r, g, b)

    def set_place(self, place_id: int, object_id: int, instance_id: int):
        self.send_tag('W_PLACE', place_id, object_id, instance_id)

    def set_view_mode(self, mode: ViewMode):
        self.send_tag('P_VIEW', mode.value)

    def lock_view(self, lock: bool):
        self.send_tag('P_LOCKVIEW', int(lock))

    def lock_scroll(self, lock: bool):
        self.send_tag('P_LOCKSCROLL', int(lock))

    def lock_camera(self, lock: bool):
        self.send_tag('P_LOCKCAMERA', int(lock))

    def lock_zoom(self, lock: bool):
        self.send_tag('P_LOCKZOOM', int(lock))

    def set_elevation_scale(self, scale: float):
        self.send_tag('P_ELEVSCALE', scale)

    def set_terrain_lighting(self, enabled: bool):
        self.send_tag('P_RELIEF', int(enabled))

    def set_mapblock(self, type: MapblockType, data: str, index: int = 1, size: int = 1):
        self.send_tag('P_MAPBLOCK', type.value, index, size, data)

    def set_heighmap_division(self, division: float):
        self.send_tag('P_HEIGHTMAPDIVISIONS', division)

    def set_heightmap_scale(self, scale: float):
        self.send_tag('P_HEIGHTMAPSCALE', scale)

    def set_tilesize(self, size: int):
        self.send_tag('P_TILESIZE', size)

    def lock_objects(self, lock: bool):
        self.send_tag('P_LOCKOBJECTS', int(lock))

    def lock_rendersize(self, width: int, height: int, size: int = 0):
        self.send_tag('P_LOCKRENDERSIZE', size, width, height)

    def set_renderflags(self, allow_tile_occ: bool, alpha_cutoff: int):
        self.send_tag('P_RENDERFLAGS', int(allow_tile_occ), alpha_cutoff)

    def set_draggable(self, draggable: bool):
        self.send_tag('P_DRAG', int(draggable))

    def set_zoom(self, zoom: float):
        self.send_tag('P_ZOOM', zoom)

    def set_camlimits(self, top_left_x: int, top_left_y: int, bottom_right_x: int, bottom_right_y):
        self.send_tag('P_CAMLIMITS', top_left_x, top_left_y, bottom_right_x, bottom_right_y)

    def setup_camera(self, x: int, y: int, z: int, recenter: bool = True):
        self.send_tag('P_CAMERA', x, y, z, 0, int(recenter))

    def setup_camera3d(self, settings: Camera3D):
        self.send_tag('P_CAMERA3D',
           settings.near, settings.far,
           *settings.position, *settings.angle,
           settings.camera_view, settings.left,
           settings.right, settings.top,
           settings.top, settings.bottom,
           settings.aspect, settings.v_fov,
           settings.focal_length, 0, settings.camera_width,
           settings.camera_height
        )

    def send_world_type(self):
        self.send_tag('S_WORLDTYPE', self.server.server_type.value, self.server.build_type.value)

    def send_world(self):
        self.send_tag('S_WORLD',
            self.server.world_id, self.server.world_name,
            f'0:{self.place.id}', 0, 'none', 0,
            self.server.world_owner, self.server.world_name,
            0, self.server.stylesheet_id, 0
        )

    def command_received(self, command: str, args: List[Any]):
        """This method should be overridden by the protocol implementation."""
        ...
