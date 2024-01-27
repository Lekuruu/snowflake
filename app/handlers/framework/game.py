
from app.engine import Penguin, Instance
from app.objects import GameObject

@Instance.triggers.register('quit')
def quit_handler(client: Penguin, data: dict):
    client.logger.info(f'{client.name} left the game.')
    client.send_to_room()
    client.disconnected = True

@Instance.triggers.register('quitFromPayout')
def payout_handler(client: Penguin, data: dict):
    client.logger.info(f'{client.name} left the game after payout.')
    client.send_to_room()
    client.disconnected = True

@Instance.triggers.register('roomToRoomMinTime')
def on_room_to_room_min_time(client: Penguin, data: dict):
    client.is_ready = True

@Instance.triggers.register('confirmClicked')
def on_confirm_clicked(client: Penguin, data: dict):
    if client.is_ready:
        return

    confirm = GameObject.from_asset(
        'confirm',
        client.game
    )

    confirm.x = client.ninja.x + 0.5
    confirm.y = client.ninja.y + 1.05
    confirm.place_object()
    confirm.place_sprite(confirm.name)
    client.is_ready = True

    confirm.add_sound('SFX_MG_2013_CJSnow_UIPlayerReady_VBR8')
    confirm.play_sound('SFX_MG_2013_CJSnow_UIPlayerReady_VBR8', client)
