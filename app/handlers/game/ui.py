
from app.engine import Penguin, Instance
from app.data import Phase

@Instance.triggers.register('ShowMemberCardInfoTip')
def on_membercard_info_clicked(client: Penguin, data: dict):
    if client.last_tip == Phase.MEMBER_CARD:
        client.hide_tip()
        return

    client.send_tip(Phase.MEMBER_CARD)

@Instance.triggers.register('memberCardClick')
def on_membercard_select(client: Penguin, data: dict):
    if not client.is_member:
        return

    # TODO

@Instance.triggers.register('unselectMemberCard')
def on_membercard_deselect(client: Penguin, data: dict):
    if not client.is_member:
        return

    # TODO
