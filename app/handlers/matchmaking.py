
from app.engine import Penguin
from app import session

@session.framework.register('mmElementSelected')
def on_element_selected(client: Penguin, data: dict):
    client.element = data['element'].lower()
    client.tip_mode = data['tipMode']

    if client.element not in ('snow', 'water', 'fire'):
        client.logger.warning(f'Invalid element "{client.element}"')
        client.close_connection()

    client.server.matchmaking.add(client)

    for card in client.power_cards_all:
        # Card colors seem to be static for each element
        card.color = {
            'snow': 'p',
            'water': 'b',
            'fire': 'r'
        }[client.element]

@session.framework.register('mmCancel')
def on_matchmaking_cancel(client: Penguin, data: dict):
    client.server.matchmaking.remove(client)
