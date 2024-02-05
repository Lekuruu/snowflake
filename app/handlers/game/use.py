
from app.engine import Penguin
from app import session

@session.events.register('/use')
def use_handler(client: Penguin, object_id: int, x: int, y: int, local_x: float, local_y: float):
    """Sent by the client after clicking on a game object"""
    object = client.game.objects.by_id(object_id)

    if object is None:
        return

    if object.on_click is None:
        return

    object.on_click(client, object, x, y, local_x, local_y)
