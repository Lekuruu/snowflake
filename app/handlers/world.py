
from app.data import MapblockType, AlignMode, ScaleMode
from app.objects.gameobject import LocalGameObject
from app.engine.penguin import Penguin
from app import session

@session.events.register('/ready')
def ready_handler(client: Penguin):
    # Initialize window manager
    client.window_manager.load()

    # Intialize game
    client.align_ui(0, 0, AlignMode.CENTER, ScaleMode.NONE)
    client.set_background_color(34, 164, 243)
    client.set_place(client.place.id, 1, 0)

    client.set_mapblock(MapblockType.TILEMAP, client.place.mapblocks.tilemap)
    client.set_mapblock(MapblockType.HEIGHTMAP, client.place.mapblocks.heightmap)
    client.set_heighmap_division(client.place.camera.height_map_divisions)
    client.set_heightmap_scale(client.place.camera.height_map_scale)

    client.set_view_mode(client.place.camera.view_mode)
    client.set_tilesize(client.place.camera.tile_size)

    client.set_renderflags(client.place.render.occlude_tiles, client.place.render.alpha_cutoff)
    client.lock_rendersize(client.place.camera3d.camera_width, client.place.camera3d.camera_height)
    client.send_tag('P_ASSETSCOMPLETE')

    # TODO: Add more game setup tags

@session.events.register('/place_ready')
def on_place_ready(client: Penguin):
    client.send_tag('P_CAMERA', *client.place.camera.position, 0, 1)
    client.send_tag('P_ZOOM', client.place.camera.zoom)
    client.send_tag('P_LOCKCAMERA', client.place.camera.lock_view)
    client.send_tag('P_LOCKZOOM', client.place.camera.lock_zoom)

    player_object = LocalGameObject(
        client=client,
        name='Player',
        x=5,
        y=2.5
    )

    player_object.place_object()
    player_object.set_camera_target()

@session.framework.register('screenSize')
def screen_size_handler(client: Penguin, data: dict):
    client.screen_size = data['smallViewEnabled']
