
from app.engine import Penguin, Instance
from app.objects import GameObject

@Instance.triggers.register('roomToRoomMinTime')
def on_room_to_room_min_time(client: Penguin, data: dict):
    client.is_ready = True

@Instance.triggers.register('roomToRoomComplete')
def on_room_to_room_complete(client: Penguin, data: dict):
    ...

@Instance.triggers.register('roomToRoomScreenClosed')
def on_room_to_room_screen_closed(client: Penguin, data: dict):
    ...
