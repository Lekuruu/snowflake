
from app.engine import Penguin
from app.data import TipPhase
from app import session

@session.framework.register('cardClick')
def on_card_clicked(client: Penguin, data: dict):
    if not client.game.timer.running:
        return

    if client.is_ready:
        return

    if client.selected_member_card:
        client.member_card.selected = False
        client.member_card.remove()

    element = data['element']
    value = data['value']
    id = data['cardId']

    if not (card := client.power_card_by_id(id)):
        return

    if card.value != value:
        return

    if card.element != element:
        return

    card.object.x = -1
    card.object.y = -1

    client.selected_card = card
    client.ninja.remove_targets()
    client.game.grid.change_tile_sprites_for_client(client, 'ui_tile_attack', ignore_objects=True)

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
    client.game.grid.hide_tiles_for_client(client)
    client.game.grid.change_tile_sprites_for_client(client, 'ui_tile_move')

@session.framework.register('ConsumeCardResponse')
def on_card_consumed(client: Penguin, data: dict):
    try:
        client.power_card_slots.remove(client.selected_card)
        client.selected_card = None
    except ValueError:
        pass

    if not client.has_power_cards:
        snow_ui = client.get_window('cardjitsu_snowui.swf')
        snow_ui.send_payload('noCards')

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

    if not client.member_card:
        return

    if not client.game.timer.running:
        return

    if client.is_ready:
        return

    if client.selected_card:
        client.selected_card.remove()
        client.selected_card = None

    client.member_card.place()
    client.ninja.remove_targets()
    client.game.grid.hide_tiles_for_client(client)

@session.framework.register('unselectMemberCard')
def on_membercard_deselect(client: Penguin, data: dict):
    if not client.is_member:
        return

    if not client.game.timer.running:
        return

    if client.is_ready:
        return

    if not client.member_card:
        return

    client.member_card.selected = False
    client.member_card.remove()
    client.ninja.show_targets()
    client.game.grid.change_tile_sprites_for_client(client, 'ui_tile_move')

@session.framework.register('comboScreenComplete')
def on_combo_screen_complete(client: Penguin, data: dict):
    ...

@session.framework.register('RewardCardResponse')
def on_card_loaded(client: Penguin, data: dict):
    ...
