
from app.engine import Penguin
from app.data import Phase
from app import session

@session.framework.register('ShowMemberCardInfoTip')
def on_membercard_info_clicked(client: Penguin, data: dict):
    if client.last_tip == Phase.MEMBER_CARD:
        client.hide_tip()
        return

    client.send_tip(Phase.MEMBER_CARD)

@session.framework.register('memberCardClick')
def on_membercard_select(client: Penguin, data: dict):
    if not client.is_member:
        return

    # TODO

@session.framework.register('unselectMemberCard')
def on_membercard_deselect(client: Penguin, data: dict):
    if not client.is_member:
        return

    # TODO
