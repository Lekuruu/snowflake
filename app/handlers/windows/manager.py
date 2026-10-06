
from app.data import EventType
from app.engine.penguin import Penguin
from app import session

import config

@session.framework.register('windowManagerReady')
def on_window_manager_ready(client: Penguin, data: dict):
    client.window_manager.ready = True

    loading_screen = client.get_window(
        url=f'{config.ASSET_BASEURL}/cjsnow_loadingscreenassets.swf',
        name='cjsnow_loadingscreenassets.swf'
    )

    wm = client.get_window('windowmanager.swf')
    wm.send_action('setWorldId', worldId=client.server.world_id)
    wm.send_action('setBaseAssetUrl', baseAssetUrl=f'{config.BASE_URL}')
    wm.send_action('setFontPath', defaultFontPath=f'{config.BASE_URL}/fonts/')

    # Set loading screen as "RoomToRoom" transition
    wm.send_action(
        'skinRoomToRoom',
        EventType.PLAY_ACTION,
        url=loading_screen.url,
        className="",
        variant=client.battle_mode
    )

    # Load error handler
    error_handler = client.get_window('cardjitsu_snowerrorhandler.swf')
    error_handler.layer = 'bottomLayer'
    error_handler.load(
        xPercent=0,
        yPercent=0,
        loadDescription=""
    )

    card_counts = client.server.data.fetch_power_card_counts(client.pid)

    # Load player select screen
    player_select = client.get_window(config.PLAYERSELECT_SWF)
    player_select.load(
        {
            'game': 'snow' if client.battle_mode == 0 else 'snowtusk',
            'name': client.name,
            'powerCardsFire': card_counts.fire,
            'powerCardsWater': card_counts.water,
            'powerCardsSnow': card_counts.snow,
            'playerSnowRank': client.object.snow_ninja_rank
        },
        loadDescription="",
        xPercent=0,
        yPercent=0
    )
