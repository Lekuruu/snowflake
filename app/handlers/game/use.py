
from app.engine import Penguin
from app import session

def local_use_handler(client: Penguin, object_id: int, x: int, y: int, local_x: float, local_y: float):
    object = client.local_objects.by_id(object_id)

    if object is None:
        return

    if object.on_click is None:
        return

    object.on_click(client, object, x, y, local_x, local_y)

@session.events.register('/use')
def use_handler(client: Penguin, object_id: int, x: int, y: int, local_x: float, local_y: float):
    """Sent by the client after clicking on a game object"""
    object = client.game.objects.by_id(object_id)

    if object is None:
        # Try to find the object in the local objects
        local_use_handler(client, object_id, x, y, local_x, local_y)
        return

    if object.on_click is None:
        if not client.selected_card:
            return

        # Client wants to place a power card
        client.ninja.place_powercard(object.x, object.y)
        return

    object.on_click(client, object, x, y, local_x, local_y)
