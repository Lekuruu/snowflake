
from app.engine import Instance, Penguin

@Instance.events.register('/use')
def use_handler(client: Penguin, object_id: int, x: int, y: int, local_x: float, local_y: float):
    ...

@Instance.events.register('/anim_done')
def on_animation_done(client: Penguin, param_1: int, param_2: int):
    ...

@Instance.events.register('/intro_anim_done')
def on_intro_done(client: Penguin):
    ...
