
from app.engine import Penguin, Instance
from app.data import Phase

@Instance.triggers.register('roomToRoomMinTime')
def on_room_to_room_min_time(client: Penguin, data: dict):
    client.is_ready = True

@Instance.triggers.register('roomToRoomComplete')
def on_room_to_room_complete(client: Penguin, data: dict):
    ...

@Instance.triggers.register('roomToRoomScreenClosed')
def on_room_to_room_screen_closed(client: Penguin, data: dict):
    if client.last_tip in (Phase.MEMBER_CARD, Phase.CARD):
        client.game.hide_tip(client)

@Instance.triggers.register('roomToRoomMemberReviveTip')
def on_room_to_room_member_revive_tip(client: Penguin, data: dict):
    # client.send_tip(Phase.MEMBER_CARD)
    ...

@Instance.triggers.register('roomToRoomMemberBuyCardsTip')
def on_room_to_room_member_buy_cards_tip(client: Penguin, data: dict):
    # client.send_tip(Phase.CARD)
    ...
