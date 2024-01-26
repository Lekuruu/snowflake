
from app.engine import Penguin, Instance
from app.data import GameData

@Instance.triggers.register('mmElementSelected')
def on_element_selected(client: Penguin, data: dict):
    client.element = data['element'].lower()
    client.tip_mode = data['tipMode']

    if client.element not in ('snow', 'water', 'fire'):
        client.logger.warning(f'Invalid element "{client.element}"')
        client.close_connection()

    client.hp = GameData['ninjas'][client.element]['hp']
    client.range = GameData['ninjas'][client.element]['range']
    client.power = GameData['ninjas'][client.element]['attack']
    client.move = GameData['ninjas'][client.element]['move']

    client.server.matchmaking.add(client)

@Instance.triggers.register('mmCancel')
def on_matchmaking_cancel(client: Penguin, data: dict):
    client.server.matchmaking.remove(client)
