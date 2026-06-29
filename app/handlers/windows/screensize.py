
from app.engine import Penguin
from app import session

@session.framework.register('screenSize')
async def screen_size_handler(client: Penguin, data: dict):
    client.screen_size = data['smallViewEnabled']
