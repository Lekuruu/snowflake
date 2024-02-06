
from app.objects import GameObject
from app.engine import Penguin
from app import session

@session.framework.register('confirmClicked')
def on_confirm_clicked(client: Penguin, data: dict):
    """Sent by the client after clicking on the confirm button"""
    if client.is_ready:
        return

    confirm = GameObject(
        client.game,
        'ui_confirm',
        x_offset=0.5,
        y_offset=1.05
    )

    confirm.x = client.ninja.x
    confirm.y = client.ninja.y
    confirm.place_object()
    confirm.place_sprite(confirm.name)
    confirm.play_sound('SFX_MG_2013_CJSnow_UIPlayerReady_VBR8')
    client.is_ready = True

    snow_ui = client.get_window('cardjitsu_snowui.swf')
    snow_ui.send_payload('disableCards')
