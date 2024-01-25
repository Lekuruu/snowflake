
from app.engine import Instance, Penguin

@Instance.events.register('/ready')
def ready_handler(client: Penguin):
    # Initialize window manager
    client.window_manager.load()

    # Intialize game
    client.initialize_game()

@Instance.events.register('/place_ready')
def on_place_ready(client: Penguin):
    # Setup camera
    client.send_tag('P_CAMERA', 4.5, 2.49333, 0, 0, 1)
    client.send_tag('P_ZOOM', 1.000000)

    # Prevent player from modifying the camera
    client.send_tag('P_LOCKCAMERA', 1)
    client.send_tag('P_LOCKZOOM', 1)

    # Set player target id
    client.send_tag('O_PLAYER', 1)
