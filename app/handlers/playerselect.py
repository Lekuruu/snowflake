
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

    client.initialize_game()

@Instance.events.register('/place_ready')
def on_place_ready(client: Penguin):
    # Setup camera
    client.send_tag('O_HERE', 1, '0:1', 0, 0, 0, 1, 0, 0, 0, '', '0:1', 0, 1, 0)
    client.send_tag('P_CAMERA', 4.5, 2.49333, 0, 0, 1)
    client.send_tag('P_ZOOM', 1.000000)

    # Prevent player from modifying the camera
    client.send_tag('P_LOCKCAMERA', 1)
    client.send_tag('P_LOCKZOOM', 1)

    # Set player target id
    client.send_tag('O_PLAYER', 1)
