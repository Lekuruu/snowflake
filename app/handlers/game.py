
from app.engine import Instance, Penguin

@Instance.events.register('/use')
def use_handler(client: Penguin, object_id: int, x: int, y: int, local_x: float, local_y: float):
    object = client.game.objects.by_id(object_id)

    if object is None:
        return

    if object.on_click is None:
        return

    object.on_click(client, object, x, y, local_x, local_y)

@Instance.events.register('/anim_done')
def on_animation_done(client: Penguin, object_id: int, handle_id: int):
    client.game.callbacks.animation_done(handle_id)

@Instance.events.register('/sound_done')
def on_sound_done(client: Penguin, object_id: int, handle_id: int):
    client.game.callbacks.sound_done(handle_id)

@Instance.events.register('/intro_anim_done')
def on_intro_done(client: Penguin):
    ...
