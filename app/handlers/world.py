
from app.data import MapblockType, AlignMode, ScaleMode
from app.objects.gameobject import LocalGameObject
from app.engine.penguin import Penguin
from app import session

@session.events.register('/ready')
def ready_handler(client: Penguin):
    if not client.window_manager.loaded:
        # Initialize window manager
        client.window_manager.load()

    # Initialize place
    client.align_windows(0, 0, AlignMode.CENTER, ScaleMode.NONE)
    client.set_background_color(34, 164, 243)
    client.set_place(client.place.id, 1, 0)

    client.set_mapblock(MapblockType.TILEMAP, client.place.mapblocks.tilemap)
    client.set_mapblock(MapblockType.HEIGHTMAP, client.place.mapblocks.heightmap)

    client.set_view_mode(client.place.camera.view_mode)
    client.set_tilesize(client.place.camera.tile_size)

    client.lock_view(client.place.camera.lock_view)
    client.lock_scroll(client.place.camera.lock_scroll)
    client.lock_objects(client.place.object_lock)

    client.set_heightmap_division(client.place.camera.height_map_divisions)
    client.set_heightmap_scale(client.place.camera.height_map_scale)
    client.set_draggable(client.place.draggable)
    client.set_elevation_scale(client.place.camera.elevation_scale)
    client.set_terrain_lighting(client.place.camera.terrain_lighting)
    client.set_heightmap_division(client.place.camera.height_map_divisions)
    client.set_heightmap_scale(client.place.camera.height_map_scale)

    client.setup_camera3d(client.place.camera3d)
    client.set_camlimits(
        client.place.camera.margin_top_left_x, client.place.camera.margin_top_left_y,
        client.place.camera.margin_bottom_right_x, client.place.camera.margin_bottom_right_y
    )

    client.set_renderflags(client.place.render.occlude_tiles, client.place.render.alpha_cutoff)
    client.lock_rendersize(client.place.camera3d.camera_width, client.place.camera3d.camera_height)
    client.setup_physics(client.place.physics)
    client.send_tag('P_ASSETSCOMPLETE')

@session.events.register('/place_ready')
def on_place_ready(client: Penguin):
    client.setup_camera(*client.place.camera.position)
    client.set_zoom(client.place.camera.zoom)
    client.lock_camera(client.place.camera.lock_view)
    client.lock_zoom(client.place.camera.lock_zoom)

    player_object = LocalGameObject(
        client=client,
        name='Player',
        x=5,
        y=2.5
    )

    player_object.place_object()
    player_object.set_camera_target()
