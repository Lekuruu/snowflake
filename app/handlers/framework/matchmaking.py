
from app.engine import Penguin, Instance
from app.data import GameData

import time

@Instance.triggers.register('mmElementSelected')
def on_element_selected(client: Penguin, data: dict):
    client.element = data['element'].lower()
    client.tip_mode = data['tipMode']

    if client.element not in ('snow', 'water', 'fire'):
        client.logger.warning(f'Invalid element "{client.element}"')
        client.close_connection()

    client.hp = GameData['Ninjas'][client.element]['HP']
    client.range = GameData['Ninjas'][client.element]['Range']
    client.power = GameData['Ninjas'][client.element]['Attack']
    client.move = GameData['Ninjas'][client.element]['Move']

    client.server.matchmaking.add(client)

@Instance.triggers.register('mmCancel')
def on_matchmaking_cancel(client: Penguin, data: dict):
    client.server.matchmaking.remove(client)
