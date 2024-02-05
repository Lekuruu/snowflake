
from app.engine import Penguin
from app import session

@session.framework.register('windowDuplicated')
def on_window_duplicated(client: Penguin, data: dict):
    # This will get sent by the client when the server tries to load a
    # window that already exists.
    # In most cases, its just the tip window.
    client.hide_tip()
