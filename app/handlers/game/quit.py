
from app.engine import Penguin
from app import session

@session.framework.register('quit')
def quit_handler(client: Penguin, data: dict):
    client.logger.info(f'{client.name} left the game')
    client.send_to_room()
    client.disconnected = True

@session.framework.register('quitFromPayout')
def payout_handler(client: Penguin, data: dict):
    client.logger.info(f'{client.name} left the game after payout')
    client.send_to_room()
    client.disconnected = True