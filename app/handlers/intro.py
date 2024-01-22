
from ..engine import Instance, Penguin

@Instance.events.register('/ready')
def ready_handler(client: Penguin):
    # Initialize window manager
    client.window_manager.load()

    # Needs to be sent to show the player select
    client.send_tag('P_MAPBLOCK', 't', 1, 1, 'iVBORw0KGgoAAAANSUhEUgAAAAkAAAAFCAAAAACyOJm3AAAADklEQVQImWNghgEGIlkADWEAiDEh28IAAAAASUVORK5CYII=')
    client.send_tag('P_MAPBLOCK', 'h', 1, 1, 'iVBORw0KGgoAAAANSUhEUgAAAAoAAAAGCAAAAADfm1AaAAAADklEQVQImWOohwMG8pgA1rMdxRJRFewAAAAASUVORK5CYII=')

    # Align player select to center
    client.send_tag('UI_ALIGN', 101, 0, 0, 'center', 'scale_none')
    client.send_tag('W_PLACE', 0, 1, 0)

    client.load_assets()

@Instance.events.register('/place_ready')
def on_place_ready(client: Penguin):
    # TODO: Camera setup
    client.send_tag('O_PLAYER', 1)
