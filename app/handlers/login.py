
from app.protocols import MetaplaceProtocol
from app.engine.penguin import Penguin
from app.data import penguins, cards
from app import session

import urllib.parse
import logging
import config

@session.events.register('/version', login_required=False)
def version_handler(client: Penguin):
    client.send_version(config.VERSION)

@session.events.register("/place_context", login_required=False)
def context_handler(client: Penguin, place_name: str, param_string: str):
    params = urllib.parse.parse_qs(param_string)

    if not (battle_mode := params.get('battleMode')):
        client.send_login_error()
        client.close_connection()
        return

    if not (asset_url := params.get('base_asset_url')):
        client.send_login_error()
        client.close_connection()
        return

    if not (place := client.server.places.get(place_name)):
        client.send_login_error()
        client.close_connection()
        return

    client.battle_mode = int(battle_mode[0])
    client.asset_url = asset_url[0]
    client.place = place

@session.events.register('/login', login_required=False)
def login_handler(client: Penguin, server_type: str, pid: int, token: str):
    if client.logged_in:
        client.logger.warning('Login attempt failed: Already logged in')
        client.send_login_error()
        client.close_connection()
        return

    if server_type.upper() != client.server.server_type.name:
        client.logger.warning(f'Login attempt failed: Invalid server type "{server_type}"')
        client.send_login_error()
        client.close_connection()
        return

    if not (penguin := penguins.fetch_by_id(pid)):
        client.logger.warning('Login attempt failed: Penguin not found')
        client.send_login_error()
        client.close_connection()
        return

    client.pid = pid
    client.token = token
    client.name = penguin.nickname
    client.object = penguin
    client.power_cards_all = cards.fetch_by_penguin_id(pid, is_power=True)

    # TODO: Check player username approval

    other_connections = client.server.players.with_id(pid)
    other_connections.remove(client)

    if other_connections:
        for player in other_connections:
            # TODO: Send error message
            player.logger.warning('Closing duplicate connection.')
            player.close_connection()

    # TODO: Validate token

    client.logger.info(f'Logged in as "{penguin.nickname}" ({penguin.id})')
    client.logger = logging.getLogger(client.name)

    client.logged_in = True
    client.send_login_message('Finalizing login')
    client.send_login_reply()

    client.set_asset_url(config.MEDIA_DOMAIN)
    client.send_world_type()
    client.send_world()

    client.send_tag('W_DISPLAYSTATE') # Is probably used for mobile
    client.send_tag('W_ASSETSCOMPLETE') # This will send the /ready command

    # Server doesn't need to check for policy file requests anymore
    client.dataReceived = super(MetaplaceProtocol, client).dataReceived
