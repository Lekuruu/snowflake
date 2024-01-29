
from app.engine import Instance, Penguin

@Instance.events.register('/anim_done')
def on_animation_done(client: Penguin, object_id: int, handle_id: int):
    """Sent by the client after an animation is done playing"""
    client.game.callbacks.animation_done(handle_id)

@Instance.events.register('/sound_done')
def on_sound_done(client: Penguin, object_id: int, handle_id: int):
    """Sent by the client after a sound is done playing"""
    ...

@Instance.events.register('/intro_anim_done')
def on_intro_done(client: Penguin):
    """Sent by the client after the initial loading screen was closed"""
    ...
