
from app.engine import Penguin
from app.data import TipPhase
from app import session

@session.framework.register('RewardCardResponse')
def on_card_loaded(client: Penguin, data: dict):
    ...

@session.framework.register('cardClick')
def on_card_clicked(client: Penguin, data: dict):
    if not client.game.timer.running:
        return

    if client.is_ready:
        return

    element = data['element']
    value = data['value']
    id = data['cardId']

    if not (card := client.get_power_card(id)):
        return

    if card.value != value:
        return

    if card.element != element:
        return

    client.selected_card = card
    client.ninja.hide_targets()
    client.game.grid.change_tile_sprites_for_client(client, 'ui_tile_attack')

@session.framework.register('unselectCard')
def on_card_deselect(client: Penguin, data: dict):
    if not client.game.timer.running:
        return

    if not client.selected_card:
        return

    if client.is_ready:
        return

    client.selected_card.remove()
    client.selected_card = None
    client.ninja.show_targets()
    client.game.grid.change_tile_sprites_for_client(client, 'ui_tile_move')

@session.framework.register('ConsumeCardResponse')
def on_card_consumed(client: Penguin, data: dict):
    if not client.selected_card:
        return

    client.power_card_slots.remove(client.selected_card)
    client.selected_card = None

@session.framework.register('cardCount')
def on_card_count(client: Penguin, data: dict):
    card_amount = data['numCards']
    # TODO

@session.framework.register('ShowMemberCardInfoTip')
def on_membercard_info_clicked(client: Penguin, data: dict):
    if client.last_tip == TipPhase.MEMBER_CARD:
        client.hide_tip()
        return

    client.send_tip(TipPhase.MEMBER_CARD)

@session.framework.register('memberCardClick')
def on_membercard_select(client: Penguin, data: dict):
    if not client.is_member:
        return

    if not client.game.timer.running:
        return

    if client.is_ready:
        return

    # TODO

@session.framework.register('unselectMemberCard')
def on_membercard_deselect(client: Penguin, data: dict):
    if not client.is_member:
        return

    if not client.game.timer.running:
        return

    if client.is_ready:
        return

    # TODO
