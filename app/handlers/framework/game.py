
from app.engine import Penguin, Instance

@Instance.triggers.register('quit')
def quit_handler(client: Penguin, data: dict):
    client.logger.info(f'{client.name} left the game.')
    client.send_to_room()
    # TODO: Handle matchmaking

@Instance.triggers.register('quitFromPayout')
def payout_handler(client: Penguin, data: dict):
    client.logger.info(f'{client.name} left the game after payout.')
    client.send_to_room()

@Instance.triggers.register('roomToRoomComplete')
def on_room_to_room_complete(client: Penguin, data: dict):
    ...

@Instance.triggers.register('roomToRoomMinTime')
def on_room_to_room_min_time(client: Penguin, data: dict):
    client.is_ready = True

@Instance.triggers.register('roomToRoomScreenClosed')
def on_room_to_room_screen_closed(client: Penguin, data: dict):
    ...
