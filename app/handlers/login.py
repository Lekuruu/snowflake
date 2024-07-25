
from app.protocols import MetaplaceProtocol
from app.engine.penguin import Penguin
from app.data import penguins, cards
from app import session

import urllib.parse
import logging
import config
import time

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
    client.send_login_message('Got /login command from user')

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

    if not penguin.approval_en or penguin.rejection_en:
        client.name = f'P{pid}'

    other_connections = client.server.players.with_id(pid)
    other_connections.remove(client)

    if other_connections:
        for player in other_connections:
            # TODO: Send error message
            player.logger.warning('Closing duplicate connection.')
            player.close_connection()

    if not config.DISABLE_AUTHENTICATION:
        session_token = session.redis.get(f'{pid}.mpsession')

        if not session_token:
            client.logger.warning('Login attempt failed: Session token expired')
            client.send_login_error()
            client.close_connection()
            return

        if token != session_token.decode():
            client.logger.warning('Login attempt failed: Invalid session token')
            client.send_login_error()
            client.close_connection()
            return

    if client.battle_mode == 1 and penguin.snow_ninja_rank < 13:
        client.logger.warning('Login attempt failed: Tried to access tusk battle without snow gem')
        client.close_connection()
        return

    client.send_login_message('Successfully verified credentials server-side')
    client.logger.info(f'Logged in as "{penguin.nickname}" ({penguin.id})')
    client.logger = logging.getLogger(client.name)

    client.logged_in = True
    client.login_time = time.time()
    client.send_login_message('Finalizing login, creating final user object')
    client.send_login_reply()

    client.set_asset_url(f'{config.MEDIA_DOMAIN}/game/mpassets')
    client.send_world_type()
    client.send_world()

    # Set client to requested place
    client.switch_place(client.place)

    # Server doesn't need to check for policy file requests anymore
    client.dataReceived = super(MetaplaceProtocol, client).dataReceived
