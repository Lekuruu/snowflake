
from app.engine import Penguin
from app.data import EventType
from app import session

import config

@session.framework.register('windowManagerReady')
def on_window_manager_ready(client: Penguin, data: dict):
    client.window_manager.ready = True

    if client.battle_mode != 0:
        client.send_error('Tusk battles are not supported yet.')
        client.send_to_room()
        return

    loading_screen = client.get_window(
        url=f'{config.MEDIA_LOCATION}/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/assets/cjsnow_loadingscreenassets.swf',
        name='cjsnow_loadingscreenassets.swf'
    )

    wm = client.get_window('windowmanager.swf')
    wm.send_action('setWorldId', worldId=client.server.world_id)
    wm.send_action('setBaseAssetUrl', baseAssetUrl=f'{config.MEDIA_LOCATION}/game/mpassets/')
    wm.send_action('setFontPath', defaultFontPath=f'{config.MEDIA_LOCATION}/game/mpassets//fonts/')

    # Set loading screen as "RoomToRoom" transition
    wm.send_action('skinRoomToRoom', EventType.PLAY_ACTION, url=loading_screen.url, className="", variant=0)

    # Load error handler
    error_handler = client.get_window('cardjitsu_snowerrorhandler.swf')
    error_handler.layer = 'bottomLayer'
    error_handler.load(
        xPercent=0,
        yPercent=0,
        loadDescription=""
    )

    # Load player select screen
    player_select = client.get_window('cardjitsu_snowplayerselect.swf')
    player_select.load(
        {
            'game': 'snow',
            'name': client.name,
            'powerCardsFire': len(client.power_cards_fire),
            'powerCardsWater': len(client.power_cards_water),
            'powerCardsSnow': len(client.power_cards_snow),
            'playerSnowRank': client.object.snow_ninja_rank
        },
        loadDescription="",
        xPercent=0,
        yPercent=0
    )
