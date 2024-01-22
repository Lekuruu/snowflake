
from app.engine import Penguin, Instance
from app.data import EventType

import config

@Instance.triggers.register('windowManagerReady')
def on_window_manager_ready(client: Penguin, data: dict):
    client.logger.debug('Loaded window manager')
    client.window_manager.ready = True

    loading_screen = client.window_manager.get_window(
        url=f'http://{config.MEDIA_LOCATION}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/windows/../assets/cjsnow_loadingscreenassets.swf',
        name='cjsnow_loadingscreenassets.swf'
    )

    wm = client.window_manager.get_window('windowmanager.swf')
    wm.send_action('setWorldId', worldId=client.server.world_id)
    wm.send_action('setBaseAssetUrl', baseAssetUrl=f'http://{config.MEDIA_LOCATION}/game/mpassets/')
    wm.send_action('setFontPath', defaultFontPath=f'http://{config.MEDIA_LOCATION}/game/mpassets//fonts/')

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
        game="snow",
        name=client.name,
        powerCardsFire=5,   # TODO
        powerCardsWater=12, # TODO
        powerCardsSnow=22,  # TODO
        loadDescription="",
        xPercent=0,
        yPercent=0
    )
