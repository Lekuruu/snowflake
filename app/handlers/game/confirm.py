
from app.engine import Penguin, Instance
from app.objects import GameObject

@Instance.triggers.register('confirmClicked')
def on_confirm_clicked(client: Penguin, data: dict):
    """Sent by the client after clicking on the confirm button"""
    if client.is_ready:
        return

    confirm = GameObject.from_asset(
        'confirm',
        client.game,
        x_offset=0.5,
        y_offset=1.05
    )

    confirm.x = client.ninja.x
    confirm.y = client.ninja.y
    confirm.place_object()
    confirm.place_sprite(confirm.name)
    client.is_ready = True

    confirm.add_sound('SFX_MG_2013_CJSnow_UIPlayerReady_VBR8')
    confirm.play_sound('SFX_MG_2013_CJSnow_UIPlayerReady_VBR8')

    snow_ui = client.window_manager.get_window('cardjitsu_snowui.swf')
    snow_ui.send_payload('disableCards')
