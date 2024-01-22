
from ..engine import Instance, Penguin

import config

@Instance.events.register('/version', login_required=False)
def version_handler(client: Penguin):
    client.send_tag('S_VERSION', config.VERSION)

@Instance.events.register("/place_context", login_required=False)
def context_handler(client: Penguin, location: str, params: str):
    # TODO: What is this?
    # location: "snow_lobby"
    # params: battleMode=0&base_asset_url=https://media1.localhost/game/mpassets/
    ...

@Instance.events.register('/login', login_required=False)
def login_handler(client: Penguin, server_type: str, pid: int, token: str):
    if client.logged_in:
        client.send_login_error(900)
        client.close_connection()
        return

    client.pid = pid
    client.token = token

    # TODO: Validate

    if server_type.upper() != Instance.server_type.name:
        client.send_login_error(900)
        client.close_connection()
        return

    client.logged_in = True
    client.send_login_message('Finalizing login')
    client.send_login_reply()

    client.send_world_type()
    client.send_world()

    client.send_tag(
        'W_BASEASSETURL',
        config.MEDIA_LOCATION
    )

    client.send_tag('W_DISPLAYSTATE') # Is probably used for mobile
    client.send_tag('W_ASSETSCOMPLETE') # This will send the /ready command
