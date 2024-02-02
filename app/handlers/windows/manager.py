
from app.engine import Penguin, Instance
from app.data import EventType

import config
import time

@Instance.triggers.register('windowManagerReady')
def on_window_manager_ready(client: Penguin, data: dict):
    client.logger.debug('Loaded window manager')
    client.window_manager.ready = True

    if client.battle_mode != 0:
        client.send_error('Tusk battles are not supported yet.')
        client.send_to_room()
        return

    loading_screen = client.window_manager.get_window(
        url=f'{config.MEDIA_LOCATION}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/assets/cjsnow_loadingscreenassets.swf',
        name='cjsnow_loadingscreenassets.swf'
    )

    wm = client.window_manager.get_window('windowmanager.swf')
    wm.send_action('setWorldId', worldId=client.server.world_id)
    wm.send_action('setBaseAssetUrl', baseAssetUrl=f'{config.MEDIA_LOCATION}/game/mpassets/')
    wm.send_action('setFontPath', defaultFontPath=f'{config.MEDIA_LOCATION}/game/mpassets//fonts/')

    # Set loading screen as "RoomToRoom" transition
    wm.send_action('skinRoomToRoom', EventType.PLAY_ACTION, url=loading_screen.url, className="", variant=0)

    # Load error handler
    error_handler = client.window_manager.get_window('cardjitsu_snowerrorhandler.swf')
    error_handler.layer = 'bottomLayer'
    error_handler.load(
        xPercent=0,
        yPercent=0,
        loadDescription=""
    )

    # Load player select screen
    player_select = client.window_manager.get_window('cardjitsu_snowplayerselect.swf')
    player_select.load(
        {
            'game': 'snow',
            'name': client.name,
            'powerCardsFire': 2,
            'powerCardsWater': 3,
            'powerCardsSnow': 4
        },
        loadDescription="",
        xPercent=0,
        yPercent=0
    )
