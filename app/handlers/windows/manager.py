
from app.data import EventType, cards
from app.engine import Penguin
from app import session

import app.session
import config

@session.framework.register('windowManagerReady')
def on_window_manager_ready(client: Penguin, data: dict):
    client.window_manager.ready = True

    if client.battle_mode != 0:
        client.send_error('Tusk battles are not supported yet.')
        client.send_to_room()
        return

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

    with app.session.database.managed_session() as session:
        fire_count = cards.fetch_power_card_count(client.pid, 'f', session=session)
        water_count = cards.fetch_power_card_count(client.pid, 'w', session=session)
        snow_count = cards.fetch_power_card_count(client.pid, 's', session=session)

    # Load player select screen
    player_select = client.get_window(config.PLAYERSELECT_SWF)
    player_select.load(
        {
            'game': 'snow',
            'name': client.name,
            'powerCardsFire': fire_count,
            'powerCardsWater': water_count,
            'powerCardsSnow': snow_count,
            'playerSnowRank': client.object.snow_ninja_rank
        },
        loadDescription="",
        xPercent=0,
        yPercent=0
    )
