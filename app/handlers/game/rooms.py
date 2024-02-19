
from app.engine import Penguin
from app import session
from app.data import (
    InputModifier,
    InputTarget,
    InputType,
    TipPhase
)

@session.framework.register('roomToRoomMinTime')
def on_room_to_room_min_time(client: Penguin, data: dict):
    if not client.in_game:
        return

    # Register /use event
    client.register_input(
        command='/use',
        input_id='/use',
        script_id='4375706:1',
        target=InputTarget.GOB,
        event=InputType.MOUSE_CLICK,
        key_modifier=InputModifier.NONE
    )

@session.framework.register('roomToRoomComplete')
def on_room_to_room_complete(client: Penguin, data: dict):
    if not client.in_game:
        return

    # Client has loaded all assets
    client.is_ready = True

@session.framework.register('roomToRoomScreenClosed')
def on_room_to_room_screen_closed(client: Penguin, data: dict):
    if client.last_tip in (TipPhase.MEMBER_CARD, TipPhase.CARD):
        client.game.hide_tip(client)

@session.framework.register('roomToRoomMemberReviveTip')
def on_room_to_room_member_revive_tip(client: Penguin, data: dict):
    # client.send_tip(Phase.MEMBER_CARD)
    ...

@session.framework.register('roomToRoomMemberBuyCardsTip')
def on_room_to_room_member_buy_cards_tip(client: Penguin, data: dict):
    # client.send_tip(Phase.CARD)
    ...
