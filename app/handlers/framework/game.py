
from app.engine import Penguin, Instance

@Instance.triggers.register('quit')
def quit_handler(client: Penguin, data: dict):
    client.logger.info(f'{client} left the game.')
    client.send_to_room()
    # TODO: Handle matchmaking

@Instance.triggers.register('quitFromPayout')
def payout_handler(client: Penguin, data: dict):
    client.logger.info(f'{client} left the game after payout.')
    client.send_to_room()
