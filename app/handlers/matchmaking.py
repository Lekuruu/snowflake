
from app.engine.cards import CardObject
from app.engine import Penguin
from app.data import cards
from app import session

@session.framework.register('mmElementSelected')
def on_element_selected(client: Penguin, data: dict):
    client.element = data['element'].lower()
    client.tip_mode = data['tipMode']

    if client.element not in ('snow', 'water', 'fire'):
        client.logger.warning(f'Invalid element "{client.element}"')
        client.close_connection()

    client.server.matchmaking.add(client)

    card_color = {
        'snow': 'p',
        'water': 'b',
        'fire': 'r'
    }[client.element]

    element_name = {
        'snow': 's',
        'water': 'w',
        'fire': 'f'
    }[client.element]

    power_cards = cards.fetch_power_cards_by_penguin_id(
        client.pid,
        element_name
    )

    for card in power_cards:
        card_object = CardObject(card, client)
        card_object.color = card_color
        client.power_cards.append(card_object)

@session.framework.register('mmCancel')
def on_matchmaking_cancel(client: Penguin, data: dict):
    client.server.matchmaking.remove(client)
