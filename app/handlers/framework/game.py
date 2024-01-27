
from app.engine import Penguin, Instance

@Instance.triggers.register('quit')
def quit_handler(client: Penguin, data: dict):
    client.logger.info(f'{client.name} left the game.')
    client.send_to_room()
    client.disconnected = True

@Instance.triggers.register('quitFromPayout')
def payout_handler(client: Penguin, data: dict):
    client.logger.info(f'{client.name} left the game after payout.')
    client.send_to_room()
    client.disconnected = True

@Instance.triggers.register('roomToRoomMinTime')
def on_room_to_room_min_time(client: Penguin, data: dict):
    client.is_ready = True
